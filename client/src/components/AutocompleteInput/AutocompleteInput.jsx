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
				value: "",
			},
			suggestions: [],
			error: "",
		};

		if (props.fetchInitialValues) {
			this.fetchInitialValues(props.value);
		}
	}

	componentDidMount() {
		this.checkNewSuggestions("", false);
	}

	get value() {
		const { controlled, value } = this.props;
		if (controlled) {
			return value;
		}

		const { value: stateValue } = this.state;
		return stateValue;
	}

	handleChange(event) {
		const { value } = event.target;
		const { input } = this.state;
		this.checkNewSuggestions(value);
		this.setState({
			input: { ...input, value },
			error: "",
		});
	}

	getExclusions() {
		const { isSingle } = this.props;
		const { value } = this.state;
		if (!value) {
			return "";
		}

		if (isSingle) {
			return value.pk;
		}

		return value.map(({ pk }) => pk).join(",");
	}

	checkNewSuggestions(value, checkDifferent = true) {
		const { value: currentValue } = this.state;
		if (checkDifferent && value === currentValue) {
			return;
		}

		const { apiBase, type } = this.props;
		getSuggestions({
			apiBase,
			query: value,
			type,
			exclude: this.getExclusions(),
		}).then((items) => {
			this.setState({
				suggestions: items,
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

		const { apiBase, type } = this.props;
		getObjects({ apiBase, pks, type }).then((items) => {
			let newValue = null;
			if (isMulti) {
				const { value: currentValue } = this.state;
				newValue = currentValue.map((val) => {
					const page = items.find((obj) => obj.pk === val.pk);
					if (!page) {
						return val;
					}

					return page;
				});
			} else {
				[newValue] = items;
			}

			this.setState({ value: newValue });

			const { onChange } = this.props;
			if (typeof onChange === "function") {
				onChange({ target: { value: newValue } });
			}
		});
	}

	handleClick(value) {
		this.setState({ error: "", value });

		const { onChange } = this.props;
		if (typeof onChange === "function") {
			onChange({ target: { value, _autocomplete: true } });
		}
	}

	handleCreate() {
		const { input } = this.state;
		const { value } = input;
		if (value.trim() === "") {
			return;
		}

		const { apiBase, type } = this.props;
		createObject({ apiBase, type, value })
			.then((data) => {
				const { isSingle, onChange } = this.props;
				const { value: stateValue } = this.state;
				const newValue = isSingle ? data : (stateValue || []).concat(data);

				this.setState({
					value: newValue,
					error: "",
				});

				if (typeof onChange === "function") {
					onChange({ target: { value: newValue } });
				}
			})
			.catch(() => {
				this.setState({
					error: `Failed to create new item "${value}".`,
				});
			});
	}

	render() {
		const { name, isSingle, onChange, labelId, canCreate: canCreateProp } = this.props;
		const { input, suggestions, error } = this.state;

		const canCreate = canCreateProp && input.value.trim() !== "";
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
				{error && <p className={nc("error-message")}>Error: {error}</p>}
			</span>
		);
	}
}

AutocompleteInput.defaultProps = {
	fetchInitialValues: false,
	controlled: false,
};

AutocompleteInput.propTypes = {
	name: PropTypes.string.isRequired,
	type: PropTypes.string.isRequired,
	canCreate: PropTypes.bool.isRequired,
	isSingle: PropTypes.bool.isRequired,
	onChange: PropTypes.func,
	fetchInitialValues: PropTypes.bool,
	apiBase: PropTypes.string.isRequired,
	controlled: PropTypes.bool,
};

export default AutocompleteInput;
