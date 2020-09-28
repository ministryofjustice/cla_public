var isValidAmount = require('../../static-src/javascripts/modules/currencyInputValidation.js').isValidAmount

test('Integer', () => {
    expect(isValidAmount("500")).toBe(true)
})

test('Decimal', () => {
    expect(isValidAmount("10.5")).toBe(true)
})

test('Amount', () => {
    expect(isValidAmount("12.34")).toBe(true)
})

test('Too many decimal places', () => {
    expect(isValidAmount("12.345")).toBe(false)
})

test('Not a number', () => {
    expect(isValidAmount("abc")).toBe(false)
    expect(isValidAmount("1twothree")).toBe(false)
    expect(isValidAmount("one2three")).toBe(false)
})

test('Input with commas and spaces', () => {
    expect(isValidAmount("1,200")).toBe(true)
    expect(isValidAmount("1,,,,2")).toBe(true)
    expect(isValidAmount("  1  3  ")).toBe(true)
    expect(isValidAmount("12, 34, 56")).toBe(true)
    expect(isValidAmount("123.4      ")).toBe(true)
})


test('Only one decimal place', () => {
    expect(isValidAmount("1.23.45")).toBe(false)
    expect(isValidAmount("12.3 45.6")).toBe(false)
})

test('No commas or space in pence', () => {
    expect(isValidAmount("1.23.45")).toBe(false)
    expect(isValidAmount("12.3 45.6")).toBe(false)
})

test('Negative amounts', () => {
    expect(isValidAmount("-32")).toBe(false)
    expect(isValidAmount("-12.34")).toBe(false)
})

test('Input with pound sign as prefix', () => {
    expect(isValidAmount("£100")).toBe(true)
    expect(isValidAmount("£435.34")).toBe(true)
    expect(isValidAmount("£435.34")).toBe(true)
    expect(isValidAmount("£5000.2")).toBe(true)
    expect(isValidAmount("£3,90   ")).toBe(true)
    expect(isValidAmount("£3,,,412.57")).toBe(true)
})