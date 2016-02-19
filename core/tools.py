import wx


class CanvasTool:
    def __init__(self):
        pass

    def on_mouse(self, panel, gc, event):
        return False

    def post_process(self, panel, source_dc, target_dc):
        pass

    def get_cursor(self):
        return wx.StockCursor(self.get_stock_cursor_id())

    def get_stock_cursor_id(self):
        return wx.CURSOR_ARROW

    @staticmethod
    def clear(gc, size):
        prev = gc.GetCompositionMode()

        gc.SetCompositionMode(wx.COMPOSITION_SOURCE)
        gc.SetBrush(wx.Brush(wx.Colour(255, 255, 255, 0)))
        gc.DrawRectangle(0, 0, size[0], size[1])

        gc.SetCompositionMode(prev)


class WebImageTool(CanvasTool):
    def __init__(self):
        CanvasTool.__init__(self)

    def get_stock_cursor_id(self):
        return wx.CURSOR_HAND

    def on_mouse(self, panel, gc, event):
        if event.LeftUp() and panel.ui.app.last_uploaded_url:
            panel.ui.app.go_to_image_link()

        return False


class DraggingTool(CanvasTool):
    def __init__(self):
        CanvasTool.__init__(self)
        self.prev_point = None

    def get_stock_cursor_id(self):
        return wx.CURSOR_BULLSEYE

    def draw_on_start(self, gc, panel, start_point):
        pass

    def draw(self, gc, panel, start_point, end_point):
        pass

    def post_process(self, panel, source_dc, target_dc):
        target_size = target_dc.Size
        target_dc.Blit(0, 0, target_size[0], target_size[1], source_dc, 0, 0)

    def on_mouse(self, panel, gc, event):
        if event.LeftDown():
            self.prev_point = (event.X, event.Y)
            self.draw_on_start(gc, panel, self.prev_point)

        if event.Dragging() and event.LeftIsDown():
            point_from = self.prev_point
            point_to = (event.X, event.Y)

            self.draw(gc, panel, point_from, point_to)
            self.prev_point = point_to

        if event.LeftUp():
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

    def post_process(self, panel, source_dc, target_dc):
        target_size = target_dc.Size
        target_dc.Blit(0, 0, target_size[0], target_size[1], source_dc, 0, 0)

    def on_mouse(self, panel, gc, event):
        if event.LeftDown():
            self.start_point = (event.X, event.Y)

        if event.Dragging() and event.LeftIsDown():
            point_to = (event.X, event.Y)

            top_left, bottom_right = self.get_rect(point_to)

            self.clear(gc, panel.get_canvas_size())
            gc.SetPen(wx.Pen(panel.ui.current_color, panel.ui.brush_size))
            self.draw(panel, gc, top_left, bottom_right)

        if event.LeftUp():
            return True

        return False


class PencilTool(DraggingTool):
    def __init__(self):
        DraggingTool.__init__(self)

    def get_stock_cursor_id(self):
        return wx.CURSOR_PENCIL

    def draw_on_start(self, gc, panel, start_point):
        gc.SetPen(wx.Pen(panel.ui.current_color))
        gc.DrawRectangle(start_point[0], start_point[1], 1, 1)

    def draw(self, gc, panel, start_point, end_point):
        gc.SetPen(wx.Pen(panel.ui.current_color))
        gc.DrawLines((start_point, end_point))


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

    def post_process(self, panel, source_dc, target_dc):
        target_size = target_dc.Size
        target_dc.Blit(0, 0, target_size[0], target_size[1], source_dc, 0, 0)

    def on_mouse(self, panel, gc, event):
        if event.LeftDown():
            self.start_point = (event.X, event.Y)

        if event.Dragging() and event.LeftIsDown():
            point_to = (event.X, event.Y)

            self.clear(gc, panel.get_canvas_size())
            gc.SetPen(wx.Pen(panel.ui.current_color, panel.ui.brush_size))
            gc.DrawLines((self.start_point, point_to))

        if event.LeftUp():
            return True

        return False


class EraserTool(DraggingTool):
    def __init__(self):
        CanvasTool.__init__(self)
        self.start_point = None
        self.points = []

    def draw_on_start(self, gc, panel, start_point):
        self.points.append(start_point)

    def draw(self, gc, panel, start_point, end_point):
        self.points.append(end_point)

        gc.SetPen(wx.Pen(wx.Colour(255, 255, 255), panel.ui.brush_size))
        gc.DrawLines((start_point, end_point))

    def post_process(self, panel, source_dc, target_dc):
        if len(self.points) > 0:
            gc = wx.GraphicsContext.Create(target_dc)
            gc.SetCompositionMode(wx.COMPOSITION_SOURCE)
            gc.SetPen(wx.Pen(wx.Colour(255, 255, 255, 0), panel.ui.brush_size))

            path = gc.CreatePath()
            path.MoveToPoint(self.points[0])

            for point in self.points:
                path.AddLineToPoint(point)

            gc.StrokePath(path)
