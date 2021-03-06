import React from 'react'
import { connect } from 'react-redux'
import { withRouter } from 'react-router'
import { Route } from 'react-router-dom'
import { PAGE } from '../helper.js'
import appFactory from '../appFactory.js'

class AppFullscreenManager extends React.Component {
  constructor (props) {
    super(props)
    this.state = {
      isMounted: false
    }
  }

  componentDidMount = () => this.setState({isMounted: true})

  render () {
    const { props } = this

    return (
      <div className='AppFullScreenManager'>
        <div id='appFullscreenContainer' />

        {this.state.isMounted && (// we must wait for the component to be fully mounted to be sure the div#appFullscreenContainer exists in DOM
          <div className='emptyDiForRoute'>
            <Route path={PAGE.ADMIN.WORKSPACE} render={() => {
              props.renderAppFullscreen({slug: 'admin_workspace_user', hexcolor: '#7d4e24', type: 'workspace'}, props.user, {})
              return null
            }} />

            <Route path={PAGE.ADMIN.USER} render={() => {
              props.renderAppFullscreen({slug: 'admin_workspace_user', hexcolor: '#7d4e24', type: 'user'}, props.user, {})
              return null
            }} />
          </div>
        )}
      </div>
    )
  }
}

const mapStateToProps = ({ user }) => ({ user })
export default connect(mapStateToProps)(withRouter(appFactory(AppFullscreenManager)))
