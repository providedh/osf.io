<%inherit file="project/project_base.mako"/>
<%def name="title()">${node['title']} Visualization</%def>

<%def name="stylesheets()">
    ${parent.stylesheets()}
    <link rel="stylesheet" href="/static/css/pages/teistats-page.css">
</%def>

## Use full page width
<%def name="container_class()">container-xxl</%def>

<button id="startstop-button" class="btn btn-default btn-sm m-l-md"><i class="fa fa-play"></i> Start</button>
<button id="reset-button" class="btn btn-default btn-sm m-l-md"><i class="fa fa-times"></i> Reset</button>
<svg id="vis-svg-container"></svg>


<%def name="javascript_bottom()">
${parent.javascript_bottom()}
<script>

    //console.log('Hello from JS');

</script>
<script src=${"/static/public/js/teistats-page.js" | webpack_asset}></script>
</%def>