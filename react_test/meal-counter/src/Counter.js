import React, { useState } from 'react'

function Counter(props) {
  return (
    <div className="row">
      <button onClick={props.increase} className="meal-button">
        {props.name}
      </button>
      <span className="counter">{props.count}</span>
    </div>
  )
}

export default Counter
