jQuery.noConflict();

function GSInviteByCSVOptionalAttributes(tableSelector, optionalMenuSelector) {
    var table=null, labels=null, titles=null, examples=null, optionalMenu=null;

    function get_most_recent_optional_column_label() {
        var lastLabel=null;
        lastLabel = table.find('.labels .col-label:last');
        return lastLabel.text();
    }

    function new_label_cell(id, label) {
        var retval=null, btn=null;
        retval = jQuery('<th class="slide col-label '+id+'" data-menu-item="'+
                       id+'">'+label+' </th>');
        btn = jQuery('<a class="muted small">(remove)</a>');
        btn.click(column_remove_clicked);
        retval.append(btn);
        return retval
   }

    function colgroup_span_incr(val) {
        var cg=null;
        cg = jQuery('#gs-group-member-invite-csv-columns-optional');
        cg.attr('span', (parseInt(cg.attr('span'))+val).toString());
    }

    function add_column(id, name) {
        var newColLabel=null, btn=null, newColLabel=null
            label=null, title=null, example=null;
        oldColLabel = get_most_recent_optional_column_label();
        newColLabel = String.fromCharCode(oldColLabel.charCodeAt(0) + 1);

        label = new_label_cell(id, newColLabel);
        // The Add-selector is actually the last cell in the row.
        labels.find('td:last').before(label);

        title = jQuery('<td class="slide '+id+'">'+name+'</td>');
        titles.find(':last').after(title);

       example = jQuery('<td class="muted slide '+id+'">Example '
                         +name+'</td>');
        examples.find(':last').after(example);

        colgroup_span_incr(1);
        get_properties_from_cells();
    }

    function menu_option_clicked(event) {
        var t=null, id=null, name=null;
        t = jQuery(event.target);
        id = t.attr('id');
        name = t.text()
        add_column(id, name);

        t.parent().addClass('disabled');
    }

    function del_col(index) {
        var i=null;
        i = index.toString();
        labels.find('th:nth-child('+i+')').remove();
        titles.find(':nth-child('+i+')').remove();
        examples.find(':nth-child('+i+')').remove();
    }

    function column_remove_clicked (event) {
        var t=null, cell=null, menuItemId=null, menuItem=null, row=null,
            i=null;

        t = jQuery(event.target);
        cell = t.parent('th');

        menuItemId = cell.attr('data-menu-item');
        menuItem = jQuery('#'+menuItemId);
        menuItem.parent().removeClass('disabled');

        row = jQuery('.col-label');
        i = row.index(cell)+2;
        del_col(i);

        colgroup_span_incr(-1);
    }

    function get_properties_from_cells() {
        var cells=null, retval=null;
        cells = table.find('.col-label');
        retval = jQuery.map(cells, function(c, i){
            var r =null;
            r = jQuery(c).attr('data-menu-item');
            return r
        });
        return retval;
    }

    function init() {
        optionalMenu = jQuery(optionalMenuSelector);
        optionalMenu.find('a')
            .removeAttr('href')
            .click(menu_option_clicked);

        table = jQuery(tableSelector);
        labels = table.find('.labels');
        titles = table.find('.titles');
        examples = table.find('.examples');
    }
    init();  // Note: automatic execution

    return {
        get_properties: function () {
            return get_properties_from_cells();
        }
    }
}

jQuery(window).load(function () {
    var menuSelector=null, tableSelector=null, attributes=null;
    menuSelector = '.dropdown-menu';
    tableSelector = '#gs-group-member-invite-csv-columns-table';
    attributes = GSInviteByCSVOptionalAttributes(tableSelector, menuSelector);
});