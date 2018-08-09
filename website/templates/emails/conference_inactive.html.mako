<%inherit file="notify_base.mako" />

<%def name="content()">
<tr>
  <td style="border-collapse: collapse;">
    Hello ${fullname},<br>
    <br>
    You recently tried to create a project on the PROVIDEDH Collaborative Platform via email, but the conference you attempted to submit to is not currently accepting new submissions. For a list of conferences, see [ ${presentations_url} ].<br>
    <br>
    Sincerely yours,<br>
    <br>
    The PROVIDEDH Robot<br>

</tr>
</%def>
