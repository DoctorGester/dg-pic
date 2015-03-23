import wx


class CanvasTool:
    def __init__(self):
        pass

    def on_mouse(self, panel, gc, event):
        return False

    @staticmethod
    def clear(gc, size):
        prev = gc.GetCompositionMode()

        # I don't know what 1 means, probably clear mode
        # I wasn't able to identify the proper constant
        gc.SetCompositionMode(1)
        gc.SetBrush(wx.Brush(wx.Colour(255, 255, 255, 0)))
        gc.DrawRectangle(0, 0, size[0], size[1])

        gc.SetCompositionMode(prev)


class PencilTool(CanvasTool):
    def __init__(self):
        CanvasTool.__init__(self)
        self.prev_point = None

    def on_mouse(self, ui, gc, event):
        if event.ButtonDown(wx.MOUSE_BTN_LEFT):
            self.prev_point = (event.X, event.Y)
            gc.SetPen(wx.Pen(ui.current_color))
            gc.DrawRectangle(event.X, event.Y, 1, 1)

        if event.Dragging():
            point_from = self.prev_point
            point_to = (event.X, event.Y)

            gc.SetPen(wx.Pen(ui.current_color))
            gc.DrawLines((point_from, point_to))

            self.prev_point = point_to

        if event.ButtonUp(wx.MOUSE_BTN_LEFT):
            return True

        return False


class PrimitiveTool(CanvasTool):
    def __init__(self):
        CanvasTool.__init__(self)
        self.start_point = None

    def get_rect(self, end_point):
        x_min = min(self.start_point[0], end_point[0])
        x_max = max(self.start_point[0], end_point[0])
        y_min = min(self.start_point[1], end_point[1])
        y_max = max(self.start_point[1], end_point[1])

        top_left = (x_min, y_min)
        bottom_right = (x_max, y_max)

        return top_left, bottom_right

    def draw(self, panel, gc, top_left, bottom_right):
        pass

    def on_mouse(self, panel, gc, event):
        if event.ButtonDown(wx.MOUSE_BTN_LEFT):
            self.start_point = (event.X, event.Y)

        if event.Dragging():
            point_to = (event.X, event.Y)

            top_left, bottom_right = self.get_rect(point_to)

            self.clear(gc, panel.get_canvas_size())
            gc.SetPen(wx.Pen(panel.ui.current_color))
            self.draw(panel, gc, top_left, bottom_right)

        if event.ButtonUp(wx.MOUSE_BTN_LEFT):
            return True

        return False


class RectangleTool(PrimitiveTool):
    def __init__(self):
        PrimitiveTool.__init__(self)

    def draw(self, panel, gc, top_left, bottom_right):
        gc.DrawRectangle(top_left[0], top_left[1], bottom_right[0] - top_left[0], bottom_right[1] - top_left[1])


class EllipsisTool(PrimitiveTool):
    def __init__(self):
        PrimitiveTool.__init__(self)

    def draw(self, panel, gc, top_left, bottom_right):
        gc.DrawEllipse(top_left[0], top_left[1], bottom_right[0] - top_left[0], bottom_right[1] - top_left[1])


class LineTool(CanvasTool):
    def __init__(self):
        CanvasTool.__init__(self)
        self.start_point = None

    def on_mouse(self, panel, gc, event):
        if event.ButtonDown(wx.MOUSE_BTN_LEFT):
            self.start_point = (event.X, event.Y)

        if event.Dragging():
            point_to = (event.X, event.Y)

            self.clear(gc, panel.get_canvas_size())
            gc.SetPen(wx.Pen(panel.ui.current_color))
            gc.DrawLines((self.start_point, point_to))

        if event.ButtonUp(wx.MOUSE_BTN_LEFT):
            return True

        return False