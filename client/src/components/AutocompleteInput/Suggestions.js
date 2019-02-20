import React, { PureComponent } from "react";
import nclassNames from "classnames";

import getUniqueId from "../../utils/getUniqueId";
import { nc } from ".";
import { SearchIcon, RightArrowIcon } from "./Icons";

const classNames = (...args) => nc(nclassNames(...args));

class Suggestions extends PureComponent {
  constructor(...args) {
    super(...args);

    this.handleKeyPress = this.handleKeyPress.bind(this);
    this.handleBlurClick = this.handleBlurClick.bind(this);
    this.handleFocus = this.handleFocus.bind(this);

    // An object to track individual suggestion items by array index.
    // This is used to look at scrolling offsets during keyboard
    // navigation.
    this.suggestionItemsElm = {};

    this.state = {
      index: 0,
      visible: false
    };
  }

  componentWillMount() {
    this.suggestionsControlsId = getUniqueId();
  }

  componentDidMount() {
    window.addEventListener("click", this.handleBlurClick);
  }

  componentWillUnmount() {
    window.removeEventListener("click", this.handleBlurClick);
  }

  componentWillReceiveProps(nextProps) {
    if (this.shouldResetIndex(nextProps)) {
      this.setState({
        index: 0
      });
    }
  }

  scrollToSuggestion(index) {
    if (!this.suggestionsElm) {
      return;
    }

    if (!this.suggestionItemsElm[index]) {
      return;
    }

    const item = this.suggestionItemsElm[index];
    const dY = item.offsetHeight;
    const containerBottom =
      this.suggestionsElm.scrollTop + this.suggestionsElm.offsetHeight;
    if (this.state.index < index && item.offsetTop > containerBottom) {
      // We only want to be movin' on down if we definitely need to scroll to
      // see the target item. This means we have to check both that its offset
      // is past where we've scrolled and the height of the container.
      this.suggestionsElm.scrollTop += dY;
    } else if (
      this.state.index > index &&
      item.offsetTop - dY > this.suggestionsElm.scrollTop
    ) {
      // Movin' on up
      this.suggestionsElm.scrollTop -= dY;
    }
  }

  /**
   * If the suggestion at the curent index has changed, the index
   * needs to be reset.
   */
  shouldResetIndex(nextProps) {
    const { suggestions } = this.props;
    if (suggestions.length === 0) {
      return true;
    }

    const { index } = this.state;
    if (index >= nextProps.suggestions.length) {
      return true;
    }

    const currentId = suggestions[index].pk;
    return nextProps.suggestions[index].pk !== currentId;
  }

  handleMouseEnter(index) {
    this.setState({ index });
  }

  handleKeyPress(event) {
    const { index } = this.state;
    const { suggestions, canCreate } = this.props;

    let visible = true;

    if (event.key === "ArrowDown") {
      // Creation takes the nth index
      const max = canCreate ? suggestions.length : suggestions.length - 1;
      const target = Math.min(max, index + 1);
      this.setState({
        index: target
      });
      this.scrollToSuggestion(target);
    } else if (event.key === "ArrowUp") {
      const target = Math.max(0, index - 1);
      this.setState({
        index: target
      });
      this.scrollToSuggestion(target);
    } else if (event.key === "Enter") {
      // Enter should add the selected item, not submit the form.
      event.stopPropagation();
      event.preventDefault();

      if (index === suggestions.length) {
        this.props.onCreate();
      } else {
        this.props.onClick(suggestions[index]);
      }
    } else if (event.key === "Escape") {
      visible = false;
    }

    this.setState({ visible });
  }

  handleBlurClick(event) {
    const inComponent =
      this.containerElm.contains(event.target) ||
      // A clicked suggestion won't end up being apart of the container
      // element. We need to manually check if the event target is apart
      // of a suggestion item.
      event.target.classList.contains("suggestions__item") ||
      (event.target.parentNode &&
        event.target.parentNode.classList.contains("suggestions__item"));
    if (!inComponent && this.state.visible) {
      this.setState({ visible: false });
    }
  }

  handleFocus() {
    this.setState({ visible: true });
  }

  render() {
    const {
      suggestions,
      canCreate,
      onClick,
      onCreate,
      onChange,
      input,
      isSingle,
      labelId
    } = this.props;

    const { visible } = this.state;

    const display = this.state.visible ? "block" : "none";

    const displayCreateItem = canCreate && input.value.trim() !== "";

    const isExpanded = visible && suggestions.length > 0;
    const activeDescendantId = isExpanded
      ? `${this.suggestionsControlsId}-${this.state.index}`
      : "";

    return (
      <span
        ref={ref => {
          this.containerElm = ref;
        }}
        className={classNames("suggestions__sub", {
          "suggestions__sub--single": isSingle
        })}
      >
        <div className={nc("search-input-container")}>
          <input
            type="text"
            className={classNames("search", {
              "search--has-input": isExpanded
            })}
            onFocus={this.handleFocus}
            onChange={onChange}
            onKeyDown={this.handleKeyPress}
            {...input}
            id={labelId}
            role="combobox"
            aria-expanded={isExpanded}
            aria-owns={this.suggestionsControlsId}
            aria-haspopup="true"
            aria-autocomplete="list"
            aria-activedescendant={activeDescendantId}
          />

          <SearchIcon className={nc("search-icon")} />

          {isExpanded && (
            <div className={nc("sr-only")} aria-live="assertive">
              {suggestions.length}
              {suggestions.length === 1 ? "suggestion" : "suggestions"} found,
              use up and down arrows to review.
            </div>
          )}
        </div>

        <ul
          className={classNames("suggestions", {
            "suggestions--populated": isExpanded
          })}
          style={{ display }}
          ref={ref => {
            this.suggestionsElm = ref;
          }}
          id={this.suggestionsControlsId}
          role="listbox"
        >
          {suggestions.map((suggestion, index) => (
            <li
              key={suggestion.pk}
              onClick={onClick.bind(null, suggestion)}
              onMouseEnter={this.handleMouseEnter.bind(this, index)}
              className={classNames("suggestions__item", {
                "suggestions__item--active": index === this.state.index
              })}
              ref={ref => {
                this.suggestionItemsElm[index] = ref;
              }}
              id={`${this.suggestionsControlsId}-${index}`}
              role="option"
            >
              <span>{suggestion.title}</span>

              <RightArrowIcon />
            </li>
          ))}

          {displayCreateItem && (
            <li
              key="create"
              onClick={onCreate}
              onMouseEnter={this.handleMouseEnter.bind(
                this,
                suggestions.length
              )}
              ref={ref => {
                this.suggestionItemsElm[suggestions.length] = ref;
              }}
              className={classNames(
                "suggestions__item",
                "suggestions__item--create",
                {
                  "suggestions__item--active":
                    suggestions.length === this.state.index
                }
              )}
              id={`${this.suggestionsControlsId}-${suggestions.length}`}
            >
              Create new “{input.value}”
            </li>
          )}
        </ul>
      </span>
    );
  }
}

export default Suggestions;
