import pygame

class NineSlice:
    def __init__(self):
        pass

    @staticmethod
    def get_nine(image, slices = (0,0,0,0), width = 64, height = 64, stretch = False):
        left, top, right, bottom = slices
        w, h = image.get_size()
        w_mid = w - (left + right)
        h_mid = h - (top + bottom)
        width_mid = width - (left + right)
        height_mid = height - (top + bottom)

        to_return = pygame.Surface((width, height))
        to_return.fill((0, 0, 0))

        repeat_w = w_mid
        while(round((width_mid / float(repeat_w)), 6) != round((width_mid / float(repeat_w)))):
            repeat_w -= 1

        repeat_h = h_mid
        while (round((height_mid / float(repeat_h)), 6) != round((height_mid / float(repeat_h)))):
            repeat_h -= 1


        # top row
        to_return.blit(image, (0,0,left, top), area=(0, 0, left, top))
        for i in range(int(width_mid / repeat_w)):
            to_return.blit(image, (left + (repeat_w * i), 0, repeat_w, top), area=(left, 0, repeat_w, top))
        to_return.blit(image, (width - right, 0, right, top), area=(w - right, 0, right, top))


        # middle row
        for i in range(int(height_mid / repeat_h)):
            to_return.blit(image, (0, top + i * repeat_h, left, repeat_h), area=(0, top, left, repeat_h))
        if (stretch):
            center_slice = pygame.Surface((w_mid, h_mid))
            center_slice.blit(image, (0,0,w_mid, h_mid), area=(left, top, w_mid, h_mid))
            to_return.blit(pygame.transform.scale(center_slice, (width_mid, height_mid)), (left, top, width_mid, height_mid))
        else:
            for i in range(int(width_mid / repeat_w)):
                for j in range(int(height_mid / repeat_h)):
                    to_return.blit(image, (left + (i * repeat_w), top + (j * repeat_h), w_mid, h_mid), area=(left, top, repeat_w, repeat_h))
        for i in range(int(height_mid / repeat_h)):
            to_return.blit(image, (width - right, top + i * repeat_h, right, repeat_h), area=(w - right, top, right, repeat_h))

        # bottom row
        to_return.blit(image, (0, height-bottom, left, bottom), area=(0, h - bottom, left, bottom))
        for i in range(int(width_mid / repeat_w)):
            to_return.blit(image, (left + (repeat_w * i), height - bottom, repeat_w, bottom), area=(left, h - bottom, repeat_w, bottom))
        to_return.blit(image, (width - right, height - bottom, right, bottom), area=(w - right, h - bottom, right, bottom))

        return to_return