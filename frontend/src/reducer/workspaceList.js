import {
  SET,
  UPDATE,
  WORKSPACE_LIST,
  USER_ROLE
} from '../action-creator.sync.js'
import { handleRouteFromApi } from '../helper.js'

export function workspaceList (state = [], action) {
  switch (action.type) {
    case `${UPDATE}/${WORKSPACE_LIST}`:
      return action.workspaceList.map(ws => ({
        id: ws.workspace_id,
        label: ws.label,
        slug: ws.slug,
        // description: ws.description, // not returned by /api/v2/users/:idUser/workspaces
        sidebarEntry: ws.sidebar_entries.map(sbe => ({
          slug: sbe.slug,
          route: handleRouteFromApi(sbe.route),
          faIcon: sbe.fa_icon,
          hexcolor: sbe.hexcolor,
          label: sbe.label
        })),
        isOpenInSidebar: false
      }))

    case `${SET}/${WORKSPACE_LIST}/isOpenInSidebar`:
      return state.map(ws => ws.id === action.workspaceId
        ? {...ws, isOpenInSidebar: action.isOpenInSidebar}
        : ws
      )

    case `${SET}/${USER_ROLE}`: // not used yet
      return state.map(ws => {
        const foundWorkspace = action.userRole.find(r => ws.id === r.workspace.id) || {role: '', subscribed_to_notif: ''}
        return {
          ...ws,
          role: foundWorkspace.role,
          notif: foundWorkspace.subscribed_to_notif
        }
      })

    case `${UPDATE}/${USER_ROLE}/SubscriptionNotif`: // not used yet
      return state.map(ws => ws.id === action.workspaceId
        ? {...ws, notif: action.subscriptionNotif}
        : ws
      )

    default:
      return state
  }
}

export default workspaceList
