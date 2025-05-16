import pygame
import numpy as np

NUM_BITMAPS = {
	0: [
		"0011100",
		"0100010",
		"1000001",
		"1001001",
		"1001001",
		"1000001",
		"1000001",
		"0100010",
		"0011100",
	],
	1: [
		"0001000",
		"0011000",
		"0101000",
		"0001000",
		"0001000",
		"0001000",
		"0001000",
		"0001000",
		"0111110",
	],
	2: [
		"0111100",
		"1000010",
		"0000010",
		"0000100",
		"0001000",
		"0010000",
		"0100000",
		"1000000",
		"1111110",
	],
	3: [
		"0011100",
		"0100010",
		"0000010",
		"0000010",
		"0001100",
		"0000010",
		"0000010",
		"0100010",
		"0011100",
	],
	4: [
		"0000100",
		"0001100",
		"0010100",
		"0100100",
		"1000100",
		"1111111",
		"0000100",
		"0000100",
		"0000100",
	],
	5: [
		"0111110",
		"0100000",
		"0100000",
		"0111100",
		"0000010",
		"0000010",
		"0000010",
		"0100010",
		"0011100",
	],
	6: [
		"0011100",
		"0100010",
		"0100000",
		"0111100",
		"0100010",
		"0100010",
		"0100010",
		"0100010",
		"0011100",
	],
	7: [
		"0111110",
		"0000010",
		"0000100",
		"0000100",
		"0001000",
		"0001000",
		"0010000",
		"0010000",
		"0010000",
	],
	8: [
		"0011100",
		"0100010",
		"0100010",
		"0100010",
		"0011100",
		"0100010",
		"0100010",
		"0100010",
		"0011100",
	],
	9: [
		"0011100",
		"0100010",
		"0100010",
		"0100010",
		"0011110",
		"0000010",
		"0000010",
		"0100010",
		"0011100",
	]
}
NUMBER_SIZE = (7, 9)

def render_number(screen, left, top, number):
	canvas = np.full((NUMBER_SIZE[0]*2+1, NUMBER_SIZE[1]), 255, dtype=np.uint8)
	if number < 10:
		bitmap = NUM_BITMAPS[number]
		for y in range(NUMBER_SIZE[1]):
			for x in range(NUMBER_SIZE[0]):
				canvas[x+4, y] = (bitmap[y][x] == '0')*255
	else:
		bitmap1 = NUM_BITMAPS[number//10]
		bitmap2 = NUM_BITMAPS[number%10]
		for y in range(NUMBER_SIZE[1]):
			for x in range(NUMBER_SIZE[0]):
				canvas[x, y] = (bitmap1[y][x] == '0')*255
				canvas[x+NUMBER_SIZE[0]+1, y] = (bitmap2[y][x] == '0')*255
	rgb_array = np.stack([canvas]*3, axis=-1)  # shape: (W, H, 3)
	surface = pygame.surfarray.make_surface(rgb_array)
	pygame.surfarray.blit_array(surface, rgb_array)
	screen.blit(surface, (left, top))

def render_vertical_numbers(screen, left, top, step, numbers):
	for num in numbers[::-1]:
		render_number(screen, left, top, num)
		top -= step

def render_horizontal_numbers(screen, left, top, step, numbers):
	for num in numbers[::-1]:
		render_number(screen, left, top, num)
		left -= step

if __name__ == "__main__":
	pygame.init()
	numbers = [13, 27, 6, 49, 58, 7]

	screen = pygame.display.set_mode((1024, 800))
	pygame.display.set_caption("Vertical Pixel Numbers")
	screen.fill((255, 255, 255))
	render_vertical_numbers(screen, 200, 180, 20, numbers)
	render_horizontal_numbers(screen, 180, 200, 20, numbers)

	running = True
	while running:
		pygame.display.flip()

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				running = False

	pygame.quit()

