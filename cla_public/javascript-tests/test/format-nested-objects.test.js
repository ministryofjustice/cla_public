var formatNestedObject = require('../../static-src/javascripts/modules/format-nested-objects').formatNestedCallbackErrors

//Bad data structure created by Django for call today
var mockBadlyNestedTimeToday = [
  ["contact_number",
    ["Test"]
  ],
  ["time", {
      "time_today": ["Test"]
    }
  ]
]

//Bad data structure created by Django for call another day
var mockBadlyNestedAnotherDay = [
  ["contact_number",
    ["Test"]
  ],
  ["time", {
      "day": ["Test"],
      "time_in_day": ["Test"]
    }
  ]
]

// Correct data structure for call another day object
var mockFormattedAnotherDay = [
  ["contact_number",
    ["Test"]
  ],
  ["time-day",
    ["Test"]
  ],
  ["time-time_in_day",
    ["Test"]
  ]
]

// Correct data structure for call today object
var mockFormattedTimeToday = [
    ["contact_number",
      ["Test"]
    ],
    ["time-time_today",
      ["Test"]
    ]
  ]

test("formatNestedCallbackErrors formats nested time today object to correct data structure", () => {
  expect(formatNestedObject(mockBadlyNestedTimeToday)).toEqual(mockFormattedTimeToday)
})

test("formatNestedCallbackErrors formats nested call another day object to correct data structure", () => {
  expect(formatNestedObject(mockBadlyNestedAnotherDay)).toEqual(mockFormattedAnotherDay)
})

test("formatNestedCallbackErrors doesn't format data without key value time being present", () => {
  //mockFormattedAnotherDay does not contain "time" as a key value in data structure
  expect(formatNestedObject(mockFormattedAnotherDay)).toEqual(mockFormattedAnotherDay)
})

test("formatNestedCallbackErrors handles more values time value with correct appended pre-fix", () => {
  var mockNewKeyValues = [
      ["time", {
        "day": ["Test"],
        "time_in_day": ["Test"],
        "foo_test": ["Test", "Test1", "Test2"],
        "bar_test": ["Test"],
      }
    ]
  ]

  // Prefix time in front of keys
  var mockFormattedNewKeyValues = [
    ["time-day",
      ["Test"]
    ],
    ["time-time_in_day",
      ["Test"]
    ],
    ["time-foo_test",
      ["Test", "Test1", "Test2"]
    ],
    ["time-bar_test",
      ["Test"],
    ]
  ]

  expect(formatNestedObject(mockNewKeyValues)).toEqual(mockFormattedNewKeyValues)
})
