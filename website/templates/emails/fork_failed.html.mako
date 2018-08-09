<%inherit file="notify_base.mako" />


<%def name="content()">
<% from website import settings %>
<tr>
  <td style="border-collapse: collapse;">

    <h3 class="text-center" style="padding: 0;margin: 30px 0 0 0;border: none;list-style: none;font-weight: 300;text-align: center;">
        An error has occurred, and the fork of <b>${title}</b> on the PROVIDEDH Collaborative Platform was not successfully created. Please log in and try this action again. If the problem persists, please email ${osf_support_email}.
    </h3>
  </td>
</tr>
</%def>
