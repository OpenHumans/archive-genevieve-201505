var createReportRow = function(reportVar, idxVar) {
  var reportTemplateHTML = $("#report-template").html();
  var templateReport = _.template(reportTemplateHTML);
  var uploadFileHTML = "File upload not complete.";
  if (reportVar.uploadfile){
    uploadFileHTML = '<a href="'+reportVar.uploadfile+'"> Download Uploaded File</a>';
  }
  var processedFileHTML= "File processing not complete.";
  if (reportVar.processedfile){
    processedFileHTML = '<a href="'+reportVar.processedfile+'"> Download Processed File</a>';
  }
  return templateReport({
    reportDataId: "genome-report-data-" + idxVar,
    reportDataClass: "genome-report-" + idxVar,
    reportDataName: reportVar.name,
    reportDataTime: reportVar.timestamp,
    reportDataUploadFile: uploadFileHTML,
    reportDataProcessedFile: processedFileHTML,
    reportDataVariants: '<a href="report/'+idxVar+'"> View Report</a>',
  });
};

var getData = function(){
  $.ajax(
    {
      url: "/genomes/get-reports/",
      dataType: "json"
    }
  ).done(function( data ) {
    $('#genome-reports-table')
    .html('');
    var obj = $.parseJSON(data);
    for (var idx in obj){
      var $rowReport = createReportRow(obj[idx].fields, obj[idx].pk);
      $("#genome-reports-table").append($rowReport);
  }
});
}

$(function() {
  setInterval(function() {
  getData();
  }, 3000);
});
