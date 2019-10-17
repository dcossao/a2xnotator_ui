from django.shortcuts import render
from .forms import SignupForm
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.template.loader import render_to_string
from .tokens import account_activation_token
from django.core.mail import EmailMessage
from django.views.generic import TemplateView
from django.shortcuts import redirect

from app import settings
from src.data import doccano_daemon as daemon


class SignupView(TemplateView):
    template_name = 'signup.html'
    form_class = SignupForm

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {'form': form, 'allow_signup': bool(settings.ALLOW_SIGNUP)})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)

        # here we make sure that a post request won't trigger a subscription in case allow_signup is False
        if not bool(settings.ALLOW_SIGNUP):
            return redirect('signup')

        # if not hasattr(settings, "EMAIL_BACKEND") and not hasattr(settings, "EMAIL_HOST"):
        #     return render(request, 'email_not_set.html')

        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = True
            user.save()
            current_site = get_current_site(request)
            mail_subject = 'Activate your account.'
            uid = urlsafe_base64_encode(force_bytes(user.pk)).decode()
            message = render_to_string('acc_active_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': uid,
                'token': account_activation_token.make_token(user),
            })
            to_email = form.cleaned_data.get('email')
            # email = EmailMessage(
            #     mail_subject, message, to=[to_email]
            # )
            # email.send()

            setup_batch(user.id)

            return render(request, 'validate_mail_address_complete.html')
        else:
            return render(request, self.template_name, {'form': form, 'allow_signup': bool(settings.ALLOW_SIGNUP)})


def setup_batch(user_id):
    import logging

    logger = logging.getLogger("test")
    # logger.error("PATH >> " + str(daemon.get_path()))
    batch_id = daemon.get_incomplete_batch()

    logger.error(int(daemon.get_incomplete_batch()))
    logger.error(user_id)
    logger.error(daemon.assign_project(int(user_id), int(daemon.get_incomplete_batch())))
