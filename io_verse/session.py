# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####


if "bpy" in locals():
    import imp
    imp.reload(model)
else:
    import bpy
    import verse as vrs
    from . import model


# VerseSession class
class VerseSession(vrs.Session):
    """
    Class Session for this Python client
    """
    
    # State of connection
    __state = 'DISCONNECTED'
    
    # Blender could be connected only to one Verse server
    __instance = None
    

    def state():
        """
        state() -> string
        Class getter of state
        """
        return __class__.__state
    

    def instance():
        """
        instance() -> object
        Class getter of instance
        """
        return __class__.__instance
    

    def __init__(self, hostname, service, flag):
        """
        __init__(hostname, service, flag) -> None
        """
        # Call __init__ from parent class to connect to Verse server
        super(VerseSession, self).__init__(hostname, service, flag)
        __class__.__state = 'CONNECTING'
        __class__.__instance = self
        self.fps = 60 # TODO: get current FPS
        # Create empty dictionary of nodes
        self.my_username = ''
        self.my_password = ''


    def __del__(self):
        """
        __del__() -> None
        """
        __class__.__state = 'DISCONNECTED'
        __class__.__instance = None


    def _receive_node_link(self, parent_node_id, child_node_id):
        """
         _receive_node_link(self, parent_node_id, child_node_id) -> None
        """
        # Call parent method to print debug information
        super(MySession, self)._receive_node_link(parent_node_id, child_node_id)
        # Call calback method of model
        child_node = model.VerseNode._receive_node_link(parent_node_id, child_node_id)
    

    def _receive_node_create(self, node_id, parent_id, user_id, custom_type):
        """
        _receive_node_create(node_id, parent_id, user_id, type) -> None
        """
        # Call parent method to print debug information
        super(MySession, self)._receive_node_create(node_id, parent_id, user_id, custom_type)
        # Call calback method of model
        node = model.VerseNode._receive_node_create(node_id, parent_id, user_id, custom_type)
        
    
    def _receive_node_destroy(self, node_id):
        """
        _receive_node_destroy(node_id) -> None
        """
        # Call parent method to print debug information
        super(MySession, self)._receive_node_destroy(node_id)
        # Call callback method of model
        node = model.VerseNode._receive_node_destroy(node_id)
        
    
    def _receive_connect_terminate(self, error):
        """
        receive_connect_terminate(error) -> none
        """
        print('receive_connect_terminate', error)
        __class__.__state = 'DISCONNECTED'
        __class__.__instance = None
        # Print error message
        bpy.ops.wm.verse_error('INVOKE_DEFAULT', error_string="Disconnected")
        # Clear dictionary of nodes
        model.VerseNode.nodes.clear()
        # TODO: stop timer
  
    
    def _receive_connect_accept(self, user_id, avatar_id):
        """
        receive_connect_accept(user_id, avatar_id) -> None
        """
        print('receive_connect_accept()', user_id, avatar_id)
        __class__.__state = 'CONNECTED'
        self.user_id = user_id
        self.avatar_id = avatar_id
        
        # Create root node
        self.root_node = model.VerseNode(node_id=0, parent=None, user_id=100, custom_type=0)

        # TODO: Create nodes with views to the scene
 
    
    def _receive_user_authenticate(self, username, methods):
        """
        receive_user_authenticate(username, methods) -> None
        Callback function for user authenticate
        """
        print('receive_user_authenticate()', username, methods)
        if username == '':
            bpy.ops.scene.verse_auth_dialog_operator('INVOKE_DEFAULT')
        else:
            if username == self.my_username:
                self.send_user_authenticate(self.my_username, vrs.UA_METHOD_PASSWORD, self.my_password)
    
    def send_connect_terminate(self):
        """
        send_connect_terminate() -> None
        
        """
        __class__.__state = 'DISCONNECTING'
        vrs.Session.send_connect_terminate(self)


# Class with timer modal operator running callback_update
class ModalTimerOperator(bpy.types.Operator):
    """Operator which runs its self from a timer"""
    bl_idname = "wm.modal_timer_operator"
    bl_label = "Modal Timer Operator"

    _timer = None

    def modal(self, context, event):
        if event.type == 'TIMER':
            vrs_session = VerseSession.instance()
            if vrs_session is not None:
                try:
                    vrs_session.callback_update()
                except vrs.VerseError:
                    del vrs_session
                    return {'CANCELLED'}
        return {'PASS_THROUGH'}

    def execute(self, context):
        self._timer = context.window_manager.event_timer_add(0.1, context.window)
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def cancel(self, context):
        context.window_manager.event_timer_remove(self._timer)
        return {'CANCELLED'}


# List of Blender classes in this submodule
classes = (
    ModalTimerOperator,
)


def register():
    """
    This method register all methods of this submodule
    """

    for c in classes:
        bpy.utils.register_class(c)


def unregister():
    """
    This method unregister all methods of this submodule
    """

    for c in classes:
        bpy.utils.unregister_class(c)
