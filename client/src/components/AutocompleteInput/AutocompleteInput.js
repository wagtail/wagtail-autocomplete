import React, { PureComponent } from "react";
import PropTypes from "prop-types";

import { nc } from ".";
import { getSuggestions, getObjects, createObject } from "../../utils/client";
import Single from "./Single";
import Multi from "./Multi";

import "./AutocompleteInput.scss";

class AutocompleteInput extends PureComponent {
  constructor(props, ...args) {
    super(props, ...args);

    this.handleClick = this.handleClick.bind(this);
    this.handleChange = this.handleChange.bind(this);
    this.handleCreate = this.handleCreate.bind(this);

    this.state = {
      value: props.value,
      input: {
        value: ""
      },
      suggestions: []
    };

    if (props.fetchInitialValues) {
      this.fetchInitialValues(props.value);
    }
  }

  componentDidMount() {
    this.checkNewSuggestions("", false);
  }

  get value() {
    if (this.props.controlled) {
      return this.props.value;
    }

    return this.state.value;
  }

  handleChange(event) {
    const { value } = event.target;
    this.checkNewSuggestions(value);
    this.setState({
      input: Object.assign({}, this.state.input, { value })
    });
  }

  getExclusions() {
    const { value } = this.state;
    if (!value) {
      return "";
    }

    if (this.props.isSingle) {
      return value.pk;
    }

    return value.map(({ pk }) => pk).join(",");
  }

  checkNewSuggestions(value, checkDifferent = true) {
    if (checkDifferent && value === this.state.value) {
      return;
    }

    getSuggestions({
      apiBase: this.props.apiBase,
      query: value,
      type: this.props.type,
      exclude: this.getExclusions()
    }).then(items => {
      this.setState({
        suggestions: items
      });
    });
  }

  fetchInitialValues(value) {
    if (!value) {
      return;
    }

    const isMulti = Array.isArray(value);
    if (isMulti && value.length === 0) {
      return;
    }

    let pks = null;
    if (isMulti) {
      pks = value.map(({ pk }) => encodeURI(pk)).join(",");
    } else {
      pks = value.pk;
    }

    getObjects({
      apiBase: this.props.apiBase,
      pks,
      type: this.props.type
    }).then(items => {
      let newValue = null;
      if (isMulti) {
        newValue = this.state.value.map(val => {
          const page = items.find(obj => obj.pk === val.pk);
          if (!page) {
            return val;
          }

          return page;
        });
      } else {
        newValue = items[0];
      }

      this.setState({ value: newValue });

      if (typeof this.props.onChange === "function") {
        this.props.onChange({ target: { value: newValue } });
      }
    });
  }

  handleClick(value) {
    this.setState({ value });

    if (typeof this.props.onChange === "function") {
      this.props.onChange({ target: { value, _autocomplete: true } });
    }
  }

  handleCreate() {
    const { value } = this.state.input;
    if (value.trim() === "") {
      return;
    }

    createObject({
      apiBase: this.props.apiBase,
      type: this.props.type,
      value
    }).then(data => {
      const newValue = this.props.isSingle
        ? data
        : (this.state.value || []).concat(data);

      this.setState({
        isLoading: false,
        value: newValue
      });

      if (typeof this.props.onChange === "function") {
        this.props.onChange({ target: { value: newValue } });
      }
    });
    this.setState({ isLoading: true });
  }

  render() {
    const { name, isSingle, onChange, labelId } = this.props;
    const { input, suggestions } = this.state;

    const canCreate = this.props.canCreate && input.value.trim() !== "";
    const useHiddenInput = typeof onChange !== "function";

    return (
      <span className={nc()}>
        {useHiddenInput && (
          <input type="hidden" value={JSON.stringify(this.value)} name={name} />
        )}

        {isSingle && (
          <Single
            input={input}
            suggestions={suggestions}
            selected={this.value}
            labelId={labelId}
            canCreate={canCreate}
            onCreate={this.handleCreate}
            onChange={this.handleChange}
            onClick={this.handleClick}
          />
        )}

        {!isSingle && (
          <Multi
            input={input}
            suggestions={suggestions}
            selections={this.value || Multi.defaultProps.selections}
            labelId={labelId}
            canCreate={canCreate}
            onCreate={this.handleCreate}
            onChange={this.handleChange}
            onClick={this.handleClick}
          />
        )}
      </span>
    );
  }
}

AutocompleteInput.defaultProps = {
  fetchInitialValues: false,
  controlled: false
};

AutocompleteInput.propTypes = {
  name: PropTypes.string.isRequired,
  type: PropTypes.string.isRequired,
  canCreate: PropTypes.bool.isRequired,
  isSingle: PropTypes.bool.isRequired,
  onChange: PropTypes.func,
  fetchInitialValues: PropTypes.bool,
  apiBase: PropTypes.string.isRequired,
  controlled: PropTypes.bool.isRequired
};

export default AutocompleteInput;
