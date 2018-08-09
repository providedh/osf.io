<%inherit file="notify_base.mako" />

<%def name="content()">
<tr>
  <td style="border-collapse: collapse;">
    <%!
        from website import settings
    %>
    Hello ${user.fullname},<br>
    <br>
    ${referrer_name + ' has approved your access request and added you' if referrer_name else 'Your access request has been approved, and you have been added'} as a contributor to the project "<a href="${node.absolute_url}">${node.title}</a>" on PROVIDEDH.<br>
    <br>
    You will ${'not receive ' if all_global_subscriptions_none else 'be automatically subscribed to '} notification emails for this project. To change your email notification preferences, visit your project or your <a href="${settings.DOMAIN + "settings/notifications/"}">user settings</a>.<br>
    <br>
    Sincerely,<br>
    <br>
    The PROVIDEDH Team<br>
    <br>
    Want more information? Visit https://providedh.ehum.psnc.pl/ to learn about the PROVIDEDH Collaborative Platform, or https://providedh.eu/ for information about the PROVIDEDH CHIST-ERA Project.<br>
    <br>
    Questions? Email ${osf_contact_email}<br>

</tr>
</%def>

