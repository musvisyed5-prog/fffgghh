
jQuery(function ($) {

    // initialize builder
    const builder = $('#builder').formBuilder({
        showActionButtons: false,
        disableFields: [
            'button',
            'hidden',
            'header',
            'paragraph',
            'autocomplete',
            'file'
        ],
        disabledAttrs: [
            'description',   // Help Text
            'placeholder',
            'className',
            'access',
            'inline',
            'toggle',
            'maxlength',
            'min',
            'max',
            'step',
            'subtype',
            'rows',
            'multiple',
            'other',
            'label',
            'value'
        ],
        onAddField: function (fieldId) {
            // A slightly longer timeout (100ms) helps ensure the DOM is fully stable
            setTimeout(() => {
                // Find the very last field added to the stage
                const $lastField = $('.stage-wrap .form-field').last();

                // Only trigger if it's not already open (prevents toggling closed)
                if (!$lastField.hasClass('editing')) {
                    $lastField.find('.toggle-form').trigger('click');
                }
            }, 100);
        },
    });

    // load saved structure (for update page)
    let savedElement = document.getElementById("saved-structure")

    if (savedElement) {
        const saved = JSON.parse(
            document.getElementById("saved-structure").textContent
        );

        if (saved) {
            builder.promise.then(function (fb) {
                fb.actions.setData(saved);
            });
            setTimeout(() => {
                $('.stage-wrap .form-field').each(function () {
                    const $field = $(this);

                    if (!$field.hasClass('editing')) {
                        $field.find('.toggle-form').trigger('click');
                    }
                });
            }, 300);
        }
    }

    // on form submit save json
    $('#form-builder-form').on('submit', function () {
        const rawData = builder.actions.getData();
        const updatedData = rawData.map(field => {
            return {
                ...field,
                label: field.name || 'Untitled Field'
            };
        });

        const finalJson = JSON.stringify(updatedData);
        $('#id_structure').val(finalJson);
    });

});