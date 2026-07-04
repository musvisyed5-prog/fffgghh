jQuery(function ($) {

    const formData = JSON.parse(
        document.getElementById("form-json").textContent
    );

    $('#application-form').formRender({
        formData: formData
    });

});