var getData = function(){
  $.ajax(
    {
      url: "/genomes/get-reports/",
      dataType: "json"
    }
  ).done(function( data ) {
    var obj = $.parseJSON(data);
    for (var idx in obj){
      var uploadFileHTML = "File upload not complete.";
      if (obj[idx]['fields']['uploadfile']){
        uploadFileHTML = '<a href="'+obj[idx]['fields']['uploadfile']+'"> Download Uploaded File</a>';
      }
      var processedFileHTML= "File processing not complete.";
      if (obj[idx]['fields']['processedfile']){
        processedFileHTML = '<a href="'+obj[idx]['fields']['processedfile']+'"> Download Processed File</a>';
      }
      var variantsHTML= "";
      if (obj[idx]['pk']){
        variantsHTML = '<a href="report/'+obj[idx]['pk']+'"> View Report</a>';
      }
      $('#genome-reports-table')
      .append($('<tr id="report-'+obj[idx]['pk']+'">')
      .append($('<td class="report-name">'+obj[idx]['fields']['name'] + '</td>'))
      .append($('<td class="report-timestamp">'+obj[idx]['fields']['timestamp'] + '</td>'))
      .append($('<td class="report-uploadfile">'+ uploadFileHTML + '</td>'))
      .append($('<td class="report-processedfile">'+ processedFileHTML + '</td>'))
      .append($('<td class="report-variants">'+variantsHTML + '</td>'))
    );
  }
});
}

$(function(){
  getData();
});
