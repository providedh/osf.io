<script id="teiXPathRow" type="text/html">
    <tr>
        <td data-bind="attr: {class: expanded() ? 'expanded' : null, role: $root.collapsed() ? 'button' : null},
                       click: $root.collapsed() ? toggleExpand : null">
            <span class="xpath-expr m-b-xs" data-bind="text: xpath"></span>
            <span data-bind="attr: {class: expanded() ? 'fa toggle-icon fa-angle-up' : 'fa toggle-icon fa-angle-down'}"></span>
        </td>
        <td>
            <div class="header" data-bind="visible: $root.collapsed() && expanded()"></div>
            <div class="td-content" data-bind="visible: !$root.collapsed() || expanded()">
                <span class="xpath-name" data-bind="text: name"></span>
            </div>
        </td>
        <td>
            <div class="td-content" data-bind="visible: expanded() || !$root.collapsed()">
                <span data-bind="click: $root.removeXPath, visible: !$root.collapsed()"><i class="fa fa-times fa-2x remove-or-reject"></i></span>
                <button class="btn btn-default btn-sm m-l-md" data-bind="click: $root.removeXPath, visible: $root.collapsed()"><i class="fa fa-times"></i> Remove</button>
            </div>
        </td>
    </tr>
</script>
