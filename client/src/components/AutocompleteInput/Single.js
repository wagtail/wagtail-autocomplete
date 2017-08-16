import React, { PureComponent } from 'react';

import { nc } from '.';
import Suggestions from './Suggestions';


class Single extends PureComponent {
  render() {
    const {
      selected,
      onChange,
      onClick,
      onCreate,
      input,
      canCreate,
    } = this.props;

    if (selected) {
      return (
        <div className={nc('selection', 'selection--single')}>
          <span className={nc('selection__label')}>{selected.title}</span>

          <button
            type="button"
            className={nc('selection__button')}
            onClick={onClick.bind(null, null)}
          >
            <svg
              className={nc('selection__icon')}
              viewBox="0 0 1792 1792"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path d="M1490 1322q0 40-28 68l-136 136q-28 28-68 28t-68-28l-294-294-294 294q-28 28-68 28t-68-28l-136-136q-28-28-28-68t28-68l294-294-294-294q-28-28-28-68t28-68l136-136q28-28 68-28t68 28l294 294 294-294q28-28 68-28t68 28l136 136q28 28 28 68t-28 68l-294 294 294 294q28 28 28 68z" />
            </svg>

            <span className={nc('sr-only')}>Remove</span>
          </button>
        </div>
      );
    }

    const suggestions = this.props.suggestions.filter(suggestion => {
      if (!selected) {
        return true;
      }
      return suggestion.id !== selected.id;
    });

    return (
      <Suggestions
        suggestions={suggestions}
        onClick={onClick}
        onCreate={onCreate}
        onChange={onChange}
        canCreate={canCreate}
        input={input}
        isSingle={true}
      />
    );
  }
}


export default Single;
