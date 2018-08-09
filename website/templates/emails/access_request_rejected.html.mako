<%inherit file="notify_base.mako" />

<%def name="content()">
<tr>
  <td style="border-collapse: collapse;">
    <%!
        from website import settings
    %>
    Hello ${requester.fullname},<br>
    <br>
    This email is to inform you that your request for access to the project at ${node.absolute_url} has been declined.<br>
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

