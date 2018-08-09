<%inherit file="project/project_base.mako"/>
<%def name="title()">${node['title']} Analytics</%def>
<%namespace name="render_nodes" file="util/render_nodes.mako" />

<div class="page-header visible-xs">
    <h2 class="text-300">Analytics</h2>
</div>

<div class="row equal-heighted-row">
    <div class="col-sm-4 col-xs-12 panel panel-default">
        <div class="panel-body">
            <div class="text-center">
                <h3>Forks</h3>
                <h2>${node['fork_count']}</h2>
                <a href='${node['url']}forks'><h4 >View all forks</h4></a>
            </div>
        </div>
    </div>
    <div class="col-sm-4 col-xs-12">
        <div class="panel panel-default">
            <div class="panel-body">
                <div class="text-center">
                    <h3>Links to Project</h3>
                    <h2>${node['linked_nodes_count']}</h2>
                    <a data-toggle="modal" data-target="#showLinks"><h4 >View all links</h4></a>
                </div>
            </div>
        </div>
    </div>
    <div class="col-sm-4 col-xs-12 panel panel-default">
        <div class="panel-body">
            <div class="text-center">
                <h3>Template Copies</h3>
                <h2>${node['templated_count']}</h2>
            </div>
        </div>
    </div>
</div>


<%def name="stylesheets()">
  ${parent.stylesheets()}
  <link rel="stylesheet" href="/static/css/pages/statistics-page.css">
</%def>

<%def name="javascript_bottom()">
  ${parent.javascript_bottom()}
  <script>
      window.contextVars.analyticsMeta = $.extend(true, {}, window.contextVars.analyticsMeta, {
          pageMeta: {
              title: 'Analytics',
              public: true,
          },
      });
  </script>
  % if keen['public']['project_id'] and node['is_public']:
    <script>
     window.contextVars = $.extend(true, {}, window.contextVars, {
         keen: { public: { readKey: ${node['keenio_read_key'] | sjson, n} } }
     });
    </script>
    <script src="${'/static/public/js/statistics-page.js' | webpack_asset}"></script>
  % endif
</%def>
