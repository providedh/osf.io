<div id="teistatsScope">

    <p>Add at least one XPath expression for which statistics will be calculated.</p>
    <a href="#addTeiStatXPath" data-toggle="modal" class="btn btn-success btn-sm">
        <i class="fa fa-plus"></i> Add
    </a>
    
    <%include file="modal_add_xpath_expression.mako"/>

    <div class="scripted" id="teiXPathsScope">
        <table id="teiXPathTable" class="table responsive-table responsive-table-xs" data-bind="visible: visible">
            <thead>
                <tr>
                    <th class="responsive-table-hide">XPath Expression</th>
                    <th>Name</th>
                    <th class="min-width"></th>
                </tr>
            </thead>
            <tbody data-bind="template: {
                        name: 'teiXPathRow',
                        foreach: teiXPaths,
                        afterRender: afterRenderXPath
                    }">
            </tbody>
        </table>
    </div>

    <%include file="xpath_expressions_table.mako"/>

</div><!-- end #teistatsScope -->
