function stripPII(input) {
  return input.replace(/postcode=[^&]+/gi, 'postcode=[postcode]')
}
