import React, { PureComponent } from "react";

import { nc } from ".";
import { RemoveIcon } from "./Icons";
import Suggestions from "./Suggestions";

class Multi extends PureComponent {
  constructor(...args) {
    super(...args);

    this.handleClick = this.handleClick.bind(this);
  }

  handleClick(suggestion) {
    const { onClick, selections } = this.props;
    onClick(selections.concat(suggestion));
  }

  handleRemove(page) {
    const { onClick, selections } = this.props;
    onClick(selections.filter(({ pk }) => pk !== page.pk));
  }

  render() {
    const {
      selections,
      onChange,
      onCreate,
      canCreate,
      input,
      labelId
    } = this.props;

    const suggestions = this.props.suggestions.filter(suggestion => {
      if (!selections) {
        return true;
      }
      return selections.every(({ pk }) => pk !== suggestion.pk);
    });

    return (
      <span className={nc("layout")}>
        <span className={nc("layout__item")}>
          <Suggestions
            labelId={labelId}
            suggestions={suggestions}
            onClick={this.handleClick}
            onChange={onChange}
            onCreate={onCreate}
            canCreate={canCreate}
            input={input}
            inputElm={this.inputElm}
          />
        </span>

        <span className={nc("layout__item", "layout__item--padded")}>
          {selections.length === 0 && <span>Nothing selected.</span>}
          {selections.map(selection => (
            <div key={selection.pk} className={nc("selection")}>
              <span className={nc("selection__label")}>{selection.title}</span>

              <button
                type="button"
                className={nc("selection__button")}
                onClick={this.handleRemove.bind(this, selection)}
              >
                <RemoveIcon className={nc("selection__icon")} />

                <span className={nc("sr-only")}>Remove</span>
              </button>
            </div>
          ))}
        </span>
      </span>
    );
  }
}

Multi.defaultProps = {
  selections: []
};

export default Multi;
