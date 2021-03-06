import React from 'react'
import PropTypes from 'prop-types'
import Radium from 'radium'
import CardPopup from './CardPopup.jsx'

require('./CardPopupCreateContent.styl')

const PopupCreateContent = props => {
  return (
    <CardPopup
      customClass='popupCreateContent'
      customColor={props.customColor}
      onClose={props.onClose}
    >
      <div className='createcontent'>
        <div className='createcontent__contentname mb-4'>
          <div className='createcontent__contentname__icon ml-1 mr-3'>
            <i className={`fa fa-${props.faIcon}`} style={{color: props.customColor}} />
          </div>

          <div className='createcontent__contentname__title' style={{color: props.customColor}}>
            {props.label}
          </div>
        </div>

        <form className='createcontent__form'>
          <input
            type='text'
            className='createcontent__form__input'
            placeholder={props.inputPlaceholder}
            value={props.contentName}
            onChange={props.onChangeContentName}
          />

          <div className='createcontent__form__button'>
            <button
              type='button' // do neither remove this nor set it to 'submit' otherwise clicking the btn will submit the form and reload the page
              className='createcontent__form__button btn btn-primary'
              onClick={props.onValidate}
              style={{
                backgroundColor: '#fdfdfd',
                color: props.customColor,
                borderColor: props.customColor,
                ':hover': {
                  backgroundColor: props.customColor,
                  color: '#fdfdfd'
                }
              }}
            >
              {props.btnValidateLabel}
            </button>
          </div>
        </form>
      </div>
    </CardPopup>
  )
}

PopupCreateContent.propTypes = {
  onClose: PropTypes.func.isRequired,
  onValidate: PropTypes.func.isRequired,
  contentName: PropTypes.string.isRequired,
  onChangeContentName: PropTypes.func.isRequired,
  label: PropTypes.string,
  customColor: PropTypes.string,
  faIcon: PropTypes.string,
  btnValidateLabel: PropTypes.string,
  inputPlaceholder: PropTypes.string
}

PopupCreateContent.defaultProps = {
  label: '',
  customColor: '#333',
  inputPlaceHolder: '',
  btnValidateLabel: ''
}

export default Radium(PopupCreateContent)
