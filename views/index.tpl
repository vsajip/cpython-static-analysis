<%
#
# Copyright (C) 2019 Red Dove Consultants Limited. All rights reserved.
#
%>
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>CPython Static Variables Analysis Results</title>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.css" integrity="sha256-NuCn4IvuZXdBaFKJOAcsU2Q3ZpwbdFisd5dux4jkQ5w=" crossorigin="anonymous"/>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/twitter-bootstrap/3.3.7/css/bootstrap.min.css" integrity="sha256-916EbMg70RQy9LHiGkXzG8hSg9EdNy97GazNG/aiY1w=" crossorigin="anonymous"/>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/twitter-bootstrap/3.3.7/css/bootstrap-theme.css" integrity="sha256-xOpS+e/dER8z72w+qryCieOGysQI8cELAVt3MHG0phY=" crossorigin="anonymous" />
<!-- link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/datatables/1.10.19/css/dataTables.bootstrap.min.css" integrity="sha256-PbaYLBab86/uCEz3diunGMEYvjah3uDFIiID+jAtIfw=" crossorigin="anonymous" / -->
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/datatables/1.10.19/css/jquery.dataTables.min.css" integrity="sha256-YY1izqyhIj4W3iyJOaGWOpXDSwrHWFL4Nfk+W0LyCHE=" crossorigin="anonymous" />
<link href="https://fonts.googleapis.com/css?family=Open+Sans|Source+Code+Pro|Source+Sans+Pro|Source+Serif+Pro|Roboto|Roboto+Mono" rel="stylesheet">
<link href="https://fonts.red-dove.com/iosevka-ss09-regular/webfont.css" rel="stylesheet">
<style>
body {
  font-family: "Trebuchet MS";
  font-size: 14px;
}
#results {
  table-layout: fixed;
}
#results tbody td {
  font-family: "Iosevka SS09 Web", "Roboto Mono", "Source Code Pro", Consolas, monospace;
}
td.name, td.typetext, td.filename {
  white-space: nowrap;
  overflow-x: hidden;
  text-overflow: ellipsis;
}
th.sclass {
  width: 7em;
}
th.sline, th.scol, th.eline, th.ecol {
  width: 2em;
}
td.sline, td.scol, td.eline, td.ecol {
  text-align: right;
}
td.name {
  width: 26em;
}
td.typetext {
  width: 10em;
}
td.filename {
  width: 15em;
  overflow-x: hidden;
}
tfoot input {
  padding-left: 4px;
  width: 100%;
  border-radius: 4px;
}
</style>
</head>
<body>
  <div class="container">
    <div class="row clearfix">
      <div class-"col-md-12">
        <div>
            <h2>CPython Static Variables Analysis Results</h2><p>The table
            below was produced using a simplistic analysis using clang. It may
            contain false positives: it just looked at all static variable
            declarations (including those inside functions). The analysis was
            done on Linux (Ubuntu) and Windows 10, so variables specific to
            other platforms will not have been captured.</p> <p>The analysis
            code can be found at <a
            href="https://github.com/vsajip/cpython-static-analysis/"><code>https://github.com/vsajip/cpython-static-analysis/</code></a>.
            In the footer of the table below, use the input boxes to filter
            the table contents by matching to the values in the respective
            columns. Use a single leading <code>~</code> to match anything
            <em>other</em> than the following text.</code></p>
        </div>
        <div id="wait" class="text-center">Getting things ready ...</div>
        <table id="results" class="table display compact" style="display: none">
          <thead>
            <tr>
              <th class="name">Variable Name</th>
              <th class="sclass">Storage Class</th>
              <th class="type">Variable Type</th>
              <th class="filename">Filename</th>
              <th class="sline">Line</th>
              <!-- th>Column</th>
              <th>End line</th>
              <th>End col</th -->
            </tr>
          </thead>
          <tbody>
% for item in rows:
            <tr rowid="{{ item.id }}">
              <td title="{{ item.name }}">{{ item.name }}</td>
              <td>{{ item.storage_class }}</td>
              <td title="{{ item.type_text }}">{{ item.type_text }}</td>
              <td title="{{ item.filename }}"><a href="https://github.com/python/cpython/blob/master/{{ item.filename }}#L{{ item.start_line }}">{{ item.filename }}</a></td>
              <td>{{ item.start_line }}</td>
              <!-- td>{{ item.start_column }}</td>
              <td>{{ item.end_line }}</td>
              <td>{{ item.end_column }}</td -->
            </tr>
% end
          </tbody>
          <tfoot>
            <tr class="filters">
              <td>Variable Name</td>
              <td>Storage class</td>
              <td>Variable Type</td>
              <td>Filename</td>
              <td></td>
              <!-- td></td>
              <td></td>
              <td></td -->
            </tr>
          </tfoot>
        </table>
      </div>
    </div>
  </div>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/jquery/3.3.1/jquery.min.js" integrity="sha256-FgpCb/KJQlLNfOu91ta32o/NMZxltwRo8QtmkMRdAu8=" crossorigin="anonymous"></script>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/twitter-bootstrap/3.3.7/js/bootstrap.min.js" integrity="sha256-U5ZEeKfGNOja007MMD3YBI0A3OSZOQbeG6z2f2Y0hu8=" crossorigin="anonymous"></script>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/datatables/1.10.19/js/dataTables.dataTables.min.js" integrity="sha256-LANO8alhOeFp7y/QVYYZaIVGDmJVuYo1hQc4bASK9Qg=" crossorigin="anonymous"></script>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/datatables/1.10.19/js/jquery.dataTables.min.js" integrity="sha256-t5ZQTZsbQi8NxszC10CseKjJ5QeMw5NINtOXQrESGSU=" crossorigin="anonymous"></script>
  <script>
    $(document).ready(function() {
      $('#results tfoot tr.filters td').each(function() {
        var title = $(this).text();

        if (title) {
          $(this).html('<input type="text" placeholder="🔍 ' + title + '" />');
        }
      });

      var options = {
        autoWidth: false,
        dom: 'ltipr',
        lengthMenu: [20, 40, 60, 80, 100],
        columns: [
          {className: 'name'},
          null, // {className: 'sclass'},
          {className: 'typetext'},
          {className: 'filename'},
          {className: 'sline', orderable: false}
        ]
      }

      function adjust_classes() {
        $('#results thead tr .sline').removeClass('sorting_asc');
      }

      var table = $('#results').DataTable(options);

      table.columns(['.filename', '.sline']).order('asc').draw();

      adjust_classes();

      $('#wait').hide();
      $('#results').show();

      table.columns().every(function() {
        var that = this;

        $('input', this.footer()).on('keyup change clear', function() {
          var value;
          var negate = false;

          value = this.value;
          if (value[0] === '~') {
            negate = true;
            value = value.substring(1);
          }
          if (!negate) {
            if (that.search() !== value) {
              that.search(value).draw();
            }
          }
          else {
            var v = $.fn.dataTable.util.escapeRegex(value);

            that.search('^(?:(?!' + v + ').)*$', true, false).draw();
          }
          adjust_classes();
        });
      });
    });
  </script>
</body>
</html>
