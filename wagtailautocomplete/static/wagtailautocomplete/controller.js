class AutocompleteController extends window.StimulusModule.Controller {
    connect() {
        window.initAutoCompleteWidget(this.element);
    }
}

window.wagtail.app.register('autocomplete-controller', AutocompleteController);
