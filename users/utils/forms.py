from django.contrib import messages


def add_form_errors_to_messages(request, form):
    # Non-field errors (like '__all__')
    for error in form.non_field_errors():
        messages.error(request, error)

    # Field-specific errors
    for field, errors in form.errors.items():
        if field == '__all__':
            continue  # already handled
        field_obj = form.fields.get(field)
        label = field_obj.label if field_obj else field
        for error in errors:
            messages.error(request, f"{label}: {error}")