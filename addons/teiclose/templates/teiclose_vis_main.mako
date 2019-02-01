<%inherit file="project/project_base.mako"/>
<%def name="title()">${node['title']} Close Reading</%def>

<%def name="stylesheets()">
    ${parent.stylesheets()}
    <link rel="stylesheet" href="/static/css/pages/teiclose-page.css">
</%def>

## Use full page width
<%def name="container_class()">container-xxl</%def>

<div id="close-reading-widget"></div>


<%def name="javascript_bottom()">
${parent.javascript_bottom()}
<script>
// Mako variables accessible globally
    window.contextVars = $.extend(true, {}, window.contextVars, {
        file: {
            id: ${ file['id'] | sjson, n },
            filename: ${ file['filename'] | sjson, n },
            provider: ${ file['provider'] | sjson, n },
            path: ${ file['path'] | sjson, n },
            addon_url: ${ file['addon_url'] | sjson, n }
        }
    });
</script>
<script src=${"/static/public/js/teiclose-page.js" | webpack_asset}></script>
</%def>