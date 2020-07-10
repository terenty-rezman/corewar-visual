
#include <iostream>

// символ раздилителя используемый при печати в консоль, в качестве символа выбранн символ двойных кавычек "
// так как его не может быть в имени игрока м соответственно не возникнет путаницы
const char sep = '"';

// имитация Карретки
struct Carriage
{

};

// имитация Игрока
struct Player
{
	const char* name;  // имя игрока 
	const char* bytes; // код игрока, переведенный в текст, в 16 ричное представление

	Carriage* cursors; // массив кареток принадлежащих игроку
};

// печатать при создании игрока
// cycle номер текущего цикла
// player_id игроков както надо отличать друг от друга в процессе вывода, можно просто использовать аддрес их структур
// name имя игрока
// address абсолютный адресс памяти куда будет записан код игрока
// bytes код игрока переведенный в текст
void print_add_player(int cycle, const void* player_id, const char* name, int address, const char* bytes) {
	printf("p%c%d%c%p%c%s%c%d%c%s\n", sep, cycle, sep, player_id, sep, name, sep, address, sep, bytes);
}

// печатать при создании коретки
// cycle номер текущего цикла
// player_id игрок которому пренадлежит каретка
// carriage_id каретки надо отличать друг от друга, в качестве id можно использовыть адрес их структур
// address абсолютный адресс памяти где будет стартовать каретка
void print_add_carriage(int cycle, const void* player_id, const void* carriage_id, int address) {
	printf("c%c%d%c%p%c%p%c%d\n", sep, cycle, sep, player_id, sep, carriage_id, sep, address);
}

// печать при смерти карретки
// cycle номер текущего цикла
// player_id айди игрока которому пренадлежала каретка
// carriage_id айди карретки
void print_kill_carriage(int cycle, const void* player_id, const void* carriage_id) {
	printf("k%c%d%c%p%c%p\n", sep, cycle, sep, player_id, sep, carriage_id);
}

// печать при перемещении каретки
// cycle номер текущего цикла
// player_id айди игрока которому пренадлежала каретка
// carriage_id айди карретки
// offset относитьльный сдвиг - на сколько байт относительно прошлого положения переместилась каретка
void print_move_carriage(int cycle, const void* player_id, const void* carriage_id, int offset) {
	printf("m%c%d%c%p%c%p%c%d\n", sep, cycle, sep, player_id, sep, carriage_id, sep, offset);
}

// печать при записи в память игроком значения регистра (инструкция st или sti)
// cycle номер текущего цикла
// player_id айди игрока который пишет в память
// address абсолютный адресс первого байта
// значение 4х байтового регистра
void print_write_memory(int cycle, const void* player_id, int address, int32_t reg_value) {
	printf("w%c%d%c%p%c%d%c%08X\n", sep, cycle, sep, player_id, sep, address, sep, reg_value);
}

int main()
{
	// пример игрок Бэтман
	Player batman;
	batman.name = "Batman";
	batman.bytes = "4A16AF8542E561795AFABF4FCEE1F650";
	
	// пример вывода при его создании
	int cycle = 1;
	int address = 0;
	print_add_player(cycle, (void*)&batman, batman.name, address, batman.bytes);

	// пример вывода при добавлинии каретки для Бэтмана
	batman.cursors = new Carriage[2];
	cycle = 1;
	address = 0;
	print_add_carriage(cycle, (void*)&batman, (void*)&batman.cursors[0], address);

	// пример вывода при добавлинии 2ой каретки для Бэтмана
	cycle = 100;
	address = 64*20;
	print_add_carriage(cycle, (void*)&batman, (void*)&batman.cursors[1], address);

	// пример вывода при смерти 1ой каретки у Батмана
	cycle = 150;
	print_kill_carriage(cycle, (void*)&batman, (void*)&batman.cursors[0]);

	// пример вывода при перемещении 2ой каретки Бэтмана на 4 байта вперед
	cycle = 200;
	int offset = 4;
	print_move_carriage(cycle, (void*)&batman, (void*)&batman.cursors[1], offset);

	// пример записи в память игроком Бэтмен значения из регистра
	cycle = 300;
	address = 64 * 25;
	int32_t reg_value = 0x01AF223F;
	int32_t* ptr = &reg_value;
	print_write_memory(cycle, (void*)&batman, address, reg_value);

	std::cout << "done";
    
	return 0;
}