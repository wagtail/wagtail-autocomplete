import React, { PureComponent } from 'react';
import nclassNames from 'classnames';

import { nc } from '.';

import './Suggestions.scss';
import './Search.scss';


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
      visible: false,
    };
  }

  componentDidMount() {
    window.addEventListener('click', this.handleBlurClick);
  }

  componentWillUnmount() {
    window.removeEventListener('click', this.handleBlurClick);
  }

  componentWillReceiveProps(nextProps) {
    if (this.shouldResetIndex(nextProps)) {
      this.setState({
        index: 0,
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
    const containerBottom = this.suggestionsElm.scrollTop + this.suggestionsElm.offsetHeight;
    if (this.state.index < index && item.offsetTop > containerBottom) {
      // We only want to be movin' on down if we definitely need to scroll to
      // see the target item. This means we have to check both that its offset
      // is past where we've scrolled and the height of the container.
      this.suggestionsElm.scrollTop += dY;
    } else if (this.state.index > index && item.offsetTop - dY > this.suggestionsElm.scrollTop) {
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

    const currentId = suggestions[index].id;
    return nextProps.suggestions[index].id !== currentId;
  }

  handleMouseEnter(index) {
    this.setState({ index });
  }

  handleKeyPress(event) {
    const { index } = this.state;
    const { suggestions, canCreate } = this.props;

    let visible = true;

    if (event.key === 'ArrowDown') {
      // Creation takes the nth index
      const max = canCreate ? suggestions.length : suggestions.length - 1;
      const target = Math.min(max, index + 1);
      this.setState({
        index: target,
      });
      this.scrollToSuggestion(target);
    } else if (event.key === 'ArrowUp') {
      const target = Math.max(0, index - 1);
      this.setState({
        index: target,
      });
      this.scrollToSuggestion(target);
    } else if (event.key === 'Enter') {
      // Enter should add the selected item, not submit the form.
      event.stopPropagation();
      event.preventDefault();

      if (index === suggestions.length) {
        this.props.onCreate();
      } else {
        this.props.onClick(suggestions[index]);
      }
    } else if (event.key === 'Escape') {
      visible = false;
    }

    this.setState({ visible });
  }

  handleBlurClick(event) {
    const inComponent = (
      this.containerElm.contains(event.target) ||
      // A clicked suggestion won't end up being apart of the container
      // element. We need to manually check if the event target is apart
      // of a suggestion item.
      event.target.classList.contains('suggestions__item') ||
      event.target.parentNode.classList.contains('suggestions__item')
    );
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
    } = this.props;

    const { visible } = this.state;

    const display = this.state.visible ? 'block' : 'none';

    return (
      <span
        ref={ref => { this.containerElm = ref; }}
        className={classNames(
          'suggestions__sub',
          { 'suggestions__sub--single': isSingle }
        )}
      >
        <div className={nc('search-input-container')}>
          <input
            type="text"
            className={classNames(
              'search',
              { 'search--has-input': visible && suggestions.length > 0 }
            )}
            onFocus={this.handleFocus}
            onChange={onChange}
            onKeyDown={this.handleKeyPress}
            {...input}
          />

          <svg className={nc('search-icon')} viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path
              d="M15.5 14h-.79l-.28-.27C15.41 12.59 16 11.11 16 9.5 16 5.91 13.09 3 9.5 3S3 5.91 3 9.5 5.91 16 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z"
              fill="currentColor"
            />
            <path d="M0 0h24v24H0z" fill="none" />
          </svg>
        </div>

        <ul
          className={classNames(
            'suggestions',
            { 'suggestions--populated': visible && suggestions.length > 0 }
          )}
          style={{ display }}
          ref={ref => { this.suggestionsElm = ref; }}
        >
          {suggestions.map((suggestion, index) =>
            <li
              key={suggestion.id}
              onClick={onClick.bind(null, suggestion)}
              onMouseEnter={this.handleMouseEnter.bind(this, index)}
              className={classNames(
                'suggestions__item',
                { 'suggestions__item--active': index === this.state.index }
              )}
              ref={ref => { this.suggestionItemsElm[index] = ref; }}
            >
              <span>{suggestion.title}</span>

              <svg viewBox="0 0 1792 1792" xmlns="http://www.w3.org/2000/svg">
                <path d="M1600 960q0 54-37 91l-651 651q-39 37-91 37-51 0-90-37l-75-75q-38-38-38-91t38-91l293-293h-704q-52 0-84.5-37.5t-32.5-90.5v-128q0-53 32.5-90.5t84.5-37.5h704l-293-294q-38-36-38-90t38-90l75-75q38-38 90-38 53 0 91 38l651 651q37 35 37 90z" />
              </svg>
            </li>
          )}

          {canCreate && (
            <li
              key="create"
              onClick={onCreate}
              onMouseEnter={this.handleMouseEnter.bind(this, suggestions.length)}
              ref={ref => { this.suggestionItemsElm[suggestions.length] = ref; }}
              className={classNames(
                'suggestions__item',
                'suggestions__item--create',
                { 'suggestions__item--active': suggestions.length === this.state.index }
              )}
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
