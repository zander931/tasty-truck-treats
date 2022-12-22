import './App.css'
import React, { useState, useEffect } from 'react'
import hogwartsStudentRegistry from './data.js'
import AddToRegister from './Component/Register'
import CreateForm from './Component/StudentForm'
import randomSelector from './Component/RandomNum.js'

function App() {
  const [students, setStudents] = useState(hogwartsStudentRegistry)
  const [input, setInputs] = useState({
    name: '',
    house: ''
  })

  // handling both form inputs into one state
  const handleChange = (e) => {
    const StudentName = e.target.name
    let StudentHouse = e.target.value
    setInputs((prev) => {
      return { ...prev, [StudentName]: StudentHouse }
    })
  }

  // changing states

  const inputData = (e) => {
    e.preventDefault()

    let newStudentHouse = input
    const copyStudent = { ...input }
    if (input.house === 'random') {
      copyStudent.house = randomSelector()
      console.log(input)
    }
    let currentData = [copyStudent, ...students]
    setStudents(currentData)
  }

  return (
    <div className="App">
      <header className="title">Potions Class</header>
      <div className="app-wrapper">
        <div className="app-lhs-container">
          <div className="form-wrapper">
            <CreateForm handleChange={handleChange} inputData={inputData} />
          </div>
        </div>
        <div className="app-rhs-container">
          <div id="register-wrapper">
            <div id="register-component-header">
              {' '}
              <span id="star-background">ϟ</span>
              <h2 className="component-title">REGISTER</h2>
            </div>
            <div className="register-list">
              {students.map((item, id) => {
                return (
                  <AddToRegister key={id} name={item.name} house={item.house} />
                )
              })}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default App
