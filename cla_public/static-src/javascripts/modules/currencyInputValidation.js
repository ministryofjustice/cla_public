function isValidAmount(input) {
    var maxVal = 100000000
    var minVal = 0
    var pounds;
    var pence;

    var trimmedInput = input.trim()

    var decimalPointPosition = trimmedInput.indexOf('.')
    if(decimalPointPosition === -1) {
        pounds = trimmedInput
    } else {
        pounds = trimmedInput.slice(0, decimalPointPosition)
        pence = trimmedInput.slice(decimalPointPosition + 1)
    }
    pounds = pounds.replace(/^£|[\s,]+/g, "")

    if(pence) {
        if(pence.length > 2) {
            return false
        }
    }

    var amount = Number(pounds * 100)
    if(pence) {
        amount += Number(pence)
    }

    if(amount) {
        if(amount > maxVal || amount < minVal) {
            return false
        }
    } else {
        return false
    }

    return true
}

exports.isValidAmount = isValidAmount