function formatNestedObjects (errorsId) {
  var callback_id_prefix = "time-"
  // loop to check if call back time has generated any errors.
  // array generated has been re-organised.
  for (var key in errorsId) {
    if (errorsId[key][0] === "time") {
      var callback_values = errorsId[key][1]

      //Splice time and object values to create empty array.
      //empty array will be populated with new values
      errorsId[key].splice(0)
      errorsId[key].splice(1)

      for (var key1 in callback_values) {
        if (errorsId[key].length >= 2) {
          // push new array object
          errorsId.push([callback_id_prefix + key1, callback_values[key1]])
        } else {
          // push to old and empty array
          errorsId[key].push(callback_id_prefix + key1, callback_values[key1])
        }
      }
    }
  }
  return errorsId
}

exports.formatNestedCallbackErrors = formatNestedObjects
