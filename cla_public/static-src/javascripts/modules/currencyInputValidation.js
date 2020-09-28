// ($(this).val() && Number($(this).val()) > 0)

function isValidAmount(input) {
    return input && Number(input) > 0
}

exports.isValidAmount = isValidAmount