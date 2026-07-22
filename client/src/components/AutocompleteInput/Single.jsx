import React, { PureComponent } from 'react';

import { nc } from '.';
import { RemoveIcon } from './Icons';
import Suggestions from './Suggestions';


class Single extends PureComponent {
  render() {
    const {
      labelId,
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
            <RemoveIcon className={nc('selection__icon')} />

            <span className={nc('sr-only')}>Remove</span>
          </button>
        </div>
      );
    }

    const suggestions = this.props.suggestions.filter(suggestion => {
      if (!selected) {
        return true;
      }
      return suggestion.pk !== selected.pk;
    });

    return (
      <Suggestions
        labelId={labelId}
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
