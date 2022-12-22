import logo from './logo.svg'
import './App.css'
import Counter from './Counter'
import React, { useState } from 'react'

function App() {
  let [Vegetarian, setVegetarianCount] = useState(0)
  let [Vegan, setVeganCount] = useState(0)
  let [Halal, setHalalCount] = useState(0)
  let [GlutenFree, setGluetenFreeCount] = useState(0)
  let [Anything, setAnythingCount] = useState(0)

  const Increment = (name, callback) => {
    callback(name + 1)
  }

  const ResetAll = () => {
    setVegetarianCount(0)
    setVeganCount(0)
    setHalalCount(0)
    setGluetenFreeCount(0)
    setAnythingCount(0)
  }

  const mealTypes = [
    { type: 'Vegetarian', count: 0 },
    { type: 'Vegan', count: 0 },
    { type: 'Halal', count: 0 },
    { type: 'Gluten-free', count: 0 },
    { type: 'Anything!', count: 0 }
  ]

  return (
    <div className="App">
      <h1>Meal Counts</h1>
      <div class="flex-container">
        <Counter
          increase={() => {
            Increment(Vegetarian, setVegetarianCount)
          }}
          count={Vegetarian}
          name={mealTypes[0].type}
        />
        <Counter
          increase={() => {
            Increment(Vegan, setVeganCount)
          }}
          count={Vegan}
          name={mealTypes[1].type}
        />
        <Counter
          increase={() => {
            Increment(Halal, setHalalCount)
          }}
          count={Halal}
          name={mealTypes[2].type}
        />
        <Counter
          increase={() => {
            Increment(GlutenFree, setGluetenFreeCount)
          }}
          count={GlutenFree}
          name={mealTypes[3].type}
        />
        <Counter
          increase={() => {
            Increment(Anything, setAnythingCount)
          }}
          count={Anything}
          name={mealTypes[4].type}
        />

        <button
          className="remove"
          onClick={() => {
            ResetAll()
          }}
        >
          REFRESH
        </button>
      </div>
    </div>
  )
}

export default App
