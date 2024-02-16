class AutoCompleteWidgetController extends window.StimulusModule.Controller {
    connect() {
        initAutoCompleteWidget(this.element.id);
    }
}

window.wagtail.app.register('autocomplete-widget', AutoCompleteWidgetController);
