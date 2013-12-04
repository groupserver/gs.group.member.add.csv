jQuery.noConflict();

function GSInviteByCSVOptionalAttributes(tableSelector, optionalMenuSelector) {
    var table=null, labels=null, titles=null, examples=null, optionalMenu=null;

    function get_most_recent_optional_column_label() {
        var lastLabel=null;
        lastLabel = table.find('.labels .col-label:last');
        return lastLabel.text();
    }

    function colgroupSpanIncr(val) {
        var cg=null;
        cg = jQuery('#gs-group-member-invite-csv-columns-optional');
        cg.attr('span', (parseInt(cg.attr('span'))+val).toString());
    }

    function add_column(id, name) {
        var newColLabel=null, btn=null, newColLabel=null
            label=null, title=null, example=null;
        oldColLabel = get_most_recent_optional_column_label();
        newColLabel = String.fromCharCode(oldColLabel.charCodeAt(0) + 1);

        label = jQuery('<th class="slide col-label '+id+'" data-menu-item="'+
                       id+'">'+newColLabel+' </th>');

        btn = jQuery('<a class="muted small">(remove)</a>');
        btn.click(column_remove_clicked);
        label.append(btn);

        // The Add-selector is actually the last cell in the row.
        labels.find('td:last').before(label);

        title = jQuery('<td class="slide '+id+'">'+name+'</td>');
        titles.find(':last').after(title);

       example = jQuery('<td class="muted slide '+id+'">Example '
                         +name+'</td>');
        examples.find(':last').after(example);

        colgroupSpanIncr(1);
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

        colgroupSpanIncr(-1);
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
        }
    }
}

jQuery(window).load(function () {
    var menuSelector=null, tableSelector=null;
    menuSelector = '.dropdown-menu';
    tableSelector = '#gs-group-member-invite-csv-columns-table';
    GSInviteByCSVOptionalAttributes(tableSelector, menuSelector);
});