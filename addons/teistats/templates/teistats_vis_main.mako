<%inherit file="project/project_base.mako"/>
<%def name="title()">${node['title']} Visualization</%def>

<%def name="stylesheets()">
    ${parent.stylesheets()}
    <link rel="stylesheet" href="/static/css/pages/vis-container-page.css">
</%def>

## Use full page width
<%def name="container_class()">container-xxl</%def>

<svg id="vis-svg-container"></svg>


<%def name="javascript_bottom()">
${parent.javascript_bottom()}
<script>

    console.log('Hello from JS');

</script>
<script src=${"/static/public/js/vis-container-page.js" | webpack_asset}></script>
</%def>