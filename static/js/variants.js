var createVariantRow = function(genomeVar, idxVar) {
  var variantDataTemplateHTML = $("#variant-data-template").html();
  var templateVariantData = _.template(variantDataTemplateHTML);
  return templateVariantData({
    variantDataId: "genome-variant-data-" + idxVar,
    variantDataClass: "genome-variant-" + idxVar,
    variantDataChrom: genomeVar.variant_data.chrom,
    variantDataPos: genomeVar.variant_data.pos,
    variantDataRef: genomeVar.variant_data.ref_allele,
    variantDataAlt: genomeVar.variant_data.alt_allele,
    variantDataFreq: genomeVar.variant_data.freq,
    variantDataZyg: genomeVar.zyg
  });
};


var createClnvarRow = function(clnvarEntry, varData, idxEntry, idxVar) {
  var cleanedCondition = clnvarEntry.condition.replace(/\\x2c/g, ",").replace(/_/g, " ");
  var clinvarDataTemplateHTML = $("#clinvar-data-template").html();
  var templateClinvarData = _.template(clinvarDataTemplateHTML);
  return templateClinvarData({
    clinvarDataId: "clinvar-data-" + idxEntry,
    variantDataClass: "genome-variant-" + idxVar,
    clnvarClnsig: clnvarEntry.clnsig,
    clnvarEntryURL: "http://www.ncbi.nlm.nih.gov/clinvar/" +
                    clnvarEntry.accnum,
    clnvarEntryCondition: cleanedCondition,
    // TODO: file_process does not seem like the correct place for this!
    commentaryURL: "/file_process/commentary/" + clnvarEntry.id,
    exacURL: "http://exac.broadinstitute.org/variant/" +
             [varData.chrom, varData.pos, varData.ref_allele,
               varData.alt_allele].join("-")
  });
};


var getData = function() {
  $.ajax(
    {
      url: window.location.pathname + "json",
      dataType: "json"
    }
  ).done(function( data ) {
    var obj = $.parseJSON(data);
    var genomeVars = obj.genomeanalysisvariants_dataset;
    $("#genome-variants-table")
    .html('');
    for (var idx in genomeVars) {

      // Create and add row for Variant data.
      var $rowVariant = createVariantRow(genomeVars[idx], idx);
      $("#genome-variants-table").append($rowVariant);

      // Create and add a row for each ClinVar record.
      var clinvarrecords = genomeVars[idx].variant_data.clinvarrecords_dataset;
      for (var idx2 in clinvarrecords) {

        var $rowClnvar = createClnvarRow(clinvarrecords[idx2],
                                         genomeVars[idx].variant_data,
                                         idx2, idx);
        $("#genome-variants-table").append($rowClnvar);

      }
    }
  });
}

$(function() {
  getData();
  setInterval(function() {
  getData();
  }, 3000);
});
