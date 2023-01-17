from django.forms import widgets


class BootstrapFormControlMixin(object):
    """
    Twitter bootstrap is the most widely used user-interface framework. Many
    designers will have experience with it, and there are numerous off-shelf
    themes being built for marketplaces that leverage bootstrap.

    This mixin should be applied to all forms. It will add placeholder text and
    set the bootstrap "form-control" class to the widget of the field.
    """

    def __init__(self, *args, **kwargs):
        super(BootstrapFormControlMixin, self).__init__(*args, **kwargs)
        for field_name in getattr(self, "fields", ()):
            field = self.fields[field_name]

            # Which widget types don't we want to have the placeholder
            # overloaded with the title?
            if not isinstance(field.widget, (widgets.RadioSelect, widgets.MultiWidget)):
                field.widget.attrs.setdefault("placeholder", field.label)

            # Which widget types don't we want to have the class attribute set
            # to be 'form-control'?
            if not isinstance(field.widget, (widgets.RadioSelect,)):
                field.widget.attrs["class"] = "form-control"
