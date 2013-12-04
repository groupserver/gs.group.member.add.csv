jQuery.noConflict();

function GSInviteByCSVOptionalAttributes(tableSelector, optionalMenuSelector) {
    var table=null, optionalMenu=null;

    function get_most_recent_optional_column_label() {
        var lastLabel=null;
        lastLabel = table.find('.labels .col-label:last');
        return lastLabel.text();
    }

    function add_column(id, name) {
        var newColLabel=null, newColLabel=null, cg=null,
            label=null, title=null, example=null,
            labels=null, titles=null, examples=null;
        oldColLabel = get_most_recent_optional_column_label();
        newColLabel = String.fromCharCode(oldColLabel.charCodeAt(0) + 1);

        labels = table.find('.labels');
        label = jQuery('<th class="slide col-label '+id+'">'
                       +newColLabel+'</th>');
        // The Add-selector is actually the last cell in the row.
        labels.find('td:last').before(label);

        titles = table.find('.titles');
        title = jQuery('<td class="slide '+id+'">'+name+'</td>');
        titles.find(':last').after(title);

        examples = table.find('.examples');
        example = jQuery('<td class="muted slide '+id+'">Example '
                         +name+'</td>');
        examples.find(':last').after(example);

        cg = jQuery('#gs-group-member-invite-csv-columns-optional');
        cg.attr('span', (parseInt(cg.attr('span'))+1).toString());
    }

    function menu_option_clicked(event) {
        var t=null, id=null, name=null;
        t = jQuery(event.target);
        id = t.attr('id');
        name = t.text()
        add_column(id, name);

        t.parent().addClass('disabled');
    }

    function init() {
        optionalMenu = jQuery(optionalMenuSelector);
        optionalMenu.find('a')
            .removeAttr('href')
            .click(menu_option_clicked);

        table = jQuery(tableSelector);
    }
    init();  // Note: automatic execution

    return {
        get_optional_attributes: function () {}
    }
}

jQuery(window).load(function () {
    var menuSelector=null, tableSelector=null;
    menuSelector = '.dropdown-menu';
    tableSelector = '#gs-group-member-invite-csv-columns-table';
    GSInviteByCSVOptionalAttributes(tableSelector, menuSelector);
});