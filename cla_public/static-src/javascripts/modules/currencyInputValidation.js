// ($(this).val() && Number($(this).val()) > 0)

function isValidAmount(input) {
    var maxVal = 100000000
    var minVal = 0

    var value = input.split('.')
    var pounds = value[0]
    var pence = value[1]
    pounds = pounds.replaceAll(/^£|[\s,]+/g, "")

    if(pence) {
        var lengthOfPence = pence.length
        if(lengthOfPence > 2) {
            return false
        }
    }

    var amount = Number(pounds * 100)
    if(pence) {
        amount += Number(pence)
    }

    if(amount) {
        console.log('Amount: ' + amount)
        if(amount > maxVal || amount < minVal) {
            return false
        }
    } else {
        return false
    }

    return true
}

exports.isValidAmount = isValidAmount