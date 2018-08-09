<%inherit file="notify_base.mako" />

<%def name="content()">
<tr>
  <td style="border-collapse: collapse;">
    Hello ${user.fullname},<br>
    <br>
    The password for your PROVIDEDH account has successfully changed. <br>
    <br>
    If you did not request this action or you believe an unauthorized person has accessed your account, reset your password immediately by visiting:<br>
    <br>
    https://providedh.ehum.psnc.pl/settings/account/<br>
    <br>
    If you need additional help or have questions, let us know at ${osf_contact_email}.<br>
    <br>
    Sincerely yours,<br>
    <br>
    The PROVIDEDH Robot<br>

</tr>
</%def>
