<%inherit file="project/project_base.mako"/>
<%def name="title()">${node['title']} Close Reading</%def>

<%def name="stylesheets()">
    ${parent.stylesheets()}
    <link rel="stylesheet" href="/static/css/pages/teiclose-page.css">
</%def>

## Use full page width
<%def name="container_class()">container-xxl</%def>

<div>
      <section id="toolbar">
        <div class="toolbarRow" id="toolbar-controls">
          <div class="row" id="display-options">
            <span class="toolbar-control" id="">Display:
              <input id="display-uncertainty" type="checkbox"> Uncertainty
              <input id="display-annotations" type="checkbox"> Annotations
            </span>
            <span class="toolbar-control" id="">Use different colour for:
              <input id="color-uncertainty" type="checkbox"> Uncertainty types
              <input id="color-annotations" type="checkbox"> Annotation types
            </span>
          </div>
          <div class="row">
            <span class="toolbar-control" id="selected-control">
                <a id="openPanel" title="close panel" class='help'>( open )</a>
                Selected : <span id="selected"></span></span>
          </div>
        </div>
      </section>
    <section id="top-panel" class="panel">
        <div class="toolbarRow" id="toolbar-controls">
          <div class="row">
            <span class="toolbar-control" id="">
              Type <a title="help : type" class='help'>?</a> <input type="text" name="" id='type'>
              Certainty <a title="help : certainty" class='help'>?</a> <input type="text" name="" id='certainty'>
              Author <a title="help : author" class='help'>?</a> <input type="text" name="" id="author">
              Value <a title="help : value" class='help'>?</a> <input type="text" name="" id="value">
            </span>
            <span>
              <button id="create-annotation">Create</button>
            </span>
          </div>
          <div class="row">
            <span class="toolbar-control" id="">
              Proposed value <a title="help : proposed value" class='help'>?</a> <input type="text" id="proposedValue">
              Proposed type <a title="help : proposed type" class='help'>?</a> <input type="text" id="proposedType">
            </span>
            <span>
              <button id="update-annotation">Update</button>
            </span>
          </div>
          <div class="row">
            <span class="toolbar-control" id="">
              References <a title="help : references" class='help'>?</a> <input type="text" id="references" readonly>
            </span>
          </div>
          <div class="row closePanel">
              <a id="closePanel" title="close panel" class='help'>( close )</a>
          </div>
        </div>
      </section>
      <div id="stats"></div>
      <section id="editor" display-uncertainty='false' display-annotations='false' color-uncertainty='false' color-annotations='false'>

      </section>
     <div id="close-reading-widget"></div>
</div>


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
            addon_url: ${ file['addon_url'] | sjson, n },
            version: ${file['version'] | sjson, n }
        }
    });
</script>
<script src=${"/static/public/js/teiclose-page.js" | webpack_asset}></script>
</%def>