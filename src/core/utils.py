from django.core.mail import EmailMultiAlternatives
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags


def generate_image_paths(instance: dict, filename: str, prefix: str) -> str:
    """
        Generate a deterministic file name for a user's uploaded photo.

        This function is intended to be used as the `upload_to` callable for a
        Django FileField/ImageField. It renames the uploaded file using the
        instance's primary key to ensure a unique and predictable filename.

        Example:
            If instance.pk = 42 and filename = "photo.jpg",
            the stored filename will be:
                "{prefix}/42.jpg"

        Args:
            instance: The model instance to which the file is being attached.
                    Django automatically passes this when saving the file.
            filename: The original name of the uploaded file.

        Returns:
            str: A new filename in the format "<instance_pk>.<extension>".
    """

    extension = filename.split('.')[-1]
    updated_filename = f"{instance.pk}.{extension}"
    return f"{prefix}/{updated_filename}"


def get_photo_path(instance: dict, filename: str) -> str:
    return generate_image_paths(
        instance=instance,
        filename=filename,
        prefix='photos/'
    )


def get_url(request):
    current = get_current_site(request)
    protocol = "https" if request.is_secure() else "http"
    return f"{protocol}://{current.domain}"


class BaseEmailServices:

    def send(self, template, context, subject, recipients):

        html_content = render_to_string(template, context)
        text_content = strip_tags(html_content)

        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=recipients,
        )

        email.attach_alternative(html_content, "text/html")
        email.send(fail_silently=False)
