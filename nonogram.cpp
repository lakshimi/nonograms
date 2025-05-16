//------------------------------------------------------------
//	File:	SolveNemo.cpp
//	Author:	Aubrey Choi
//	Date:	2014.11.04.
//
//------------------------------------------------------------
#include <stdio.h>
#include <stdlib.h>
#include <memory.h>
#include <string.h>
#if defined(_WIN32) || defined(_WIN64)
#include <Windows.h>
#else
#include <unistd.h>
#endif

class NemoLogic
{
public:
	NemoLogic();
	~NemoLogic();

	bool Load(const char *filename);
	void InitSolve();
	bool Solve();
	bool SolveN();
	void PrintResult();
	void Print(int row);
	void PrintRow(int row);
	void PrintCol(int col);

	void ClearScreen()
	{
#if defined(_WIN32) || defined(_WIN64)
		system("cls");
#else
		printf("\033[1J");
#endif
	}

	void SetCursor(int row, int col)
	{
#if defined(_WIN32) || defined(_WIN64)
		COORD c = { col, row };
		SetConsoleCursorPosition(GetStdHandle(STD_OUTPUT_HANDLE), c);
#else
		printf("\033[%d;%dH", row+1, col+1);
#endif
	}

	int GetColNum() const { return colnum; }
	int GetRowNum() const { return rownum; }
	char *GetResult() const { return board; }

protected:
	int GetNumbers(FILE *fi, char numbers[]);
	void SetFirstPattern(char *s, const char *p);
	bool SetNextPattern(char *s, const char *p);
	bool CheckPattern(int row);
	int CheckCol(int col);
	int CheckRow(int row);

private:
	int colnum, rownum;
	char **cols, **rows;
	int phase;
	char *board;
	int totalCheck;
};

int main(int argc, char *argv[])
{
	NemoLogic logic;
	bool ret;
	char filename[128];

	printf("Enter data file name : ");
	fgets(filename, 128, stdin);
	for(int i=0;filename[i];i++) if(filename[i]=='\n') { filename[i]=0; break; }
	logic.ClearScreen();

	ret = logic.Load(filename);
	if( ret == false )
	{
		printf("Error loading %s\n", filename);
		getchar();
		return 0;
	}

	const char *s[] = { "Not solved!!! TT.", "Solved!!!" };
	logic.InitSolve();
	int r = (int)logic.SolveN();
	logic.SetCursor(logic.GetRowNum(), 0);
	puts(s[r]);
	getchar();
}

NemoLogic::NemoLogic() : cols(NULL), rows(NULL), board(NULL)
{
}

NemoLogic::~NemoLogic()
{
	if( board ) delete[] board;
	if( cols )
	{
		for( int i = 0 ; i < colnum ; i++ )
		{
			if( cols[i] ) delete[] cols[i];
		}
		delete cols;
	}
	if( rows )
	{
		for( int i = 0 ; i < rownum ; i++ )
		{
			if( rows[i] ) delete[] rows[i];
		}
		delete rows;
	}
}

bool NemoLogic::Load(const char *filename)
{
	FILE *fi = fopen(filename, "r");
	if( fi == NULL ) return false;

	char numbers[64];
	if( GetNumbers(fi, numbers) != 2 ) { fclose(fi); return false; }
	colnum = numbers[0]; rownum = numbers[1];

	cols = new char*[colnum];
	rows = new char*[rownum];

	printf("colnum = %d, rownum = %d\n", colnum, rownum);

	int rowcount = 0, colcount = 0;
	for( int i = 0 ; i < colnum ; i++ )
	{
		int count = GetNumbers(fi, numbers);
		if( count == 0 ) { fclose(fi); return false; }
		cols[i] = new char[count+1];
		memcpy(cols[i], numbers, count*sizeof(char));
		for( int j = 0 ; j < count ; j++ ) colcount += numbers[j];
		cols[i][count] = 0;
	}

	for( int i = 0 ; i < rownum ; i++ )
	{
		int count = GetNumbers(fi, numbers);
		if( count == 0 ) { fclose(fi); return false; }
		rows[i] = new char[count+1];
		memcpy(rows[i], numbers, count*sizeof(char));
		for( int j = 0 ; j < count ; j++ ) rowcount += numbers[j];
		rows[i][count] = 0;
	}

	fclose(fi);

	printf("rowcount = %d, colcount = %d\n", rowcount, colcount);
	if( rowcount != colcount ) return false;

	totalCheck = rowcount;

	return true;
}

void NemoLogic::PrintResult()
{
	SetCursor(0, 0);
	for( int i = 0 ; i < rownum ; i++ )
	{
		Print(i);
		putchar('\n');
	}
}


#if defined(_WIN32) || defined(_WIN64)
const char *s[4] = { "", "\u2593", "\u2592", "\u2591" };
#else
const char *s[4] = { "\033[0m  ", "\033[40m  ", "\033[100m  ", "\033[47m  " };
#endif
void NemoLogic::Print(int row)
{
#if defined(_WIN32) || defined(_WIN64)
	SetConsoleOutputCP(CP_UTF8);
#endif

	SetCursor(row, 0);
	for (int j = 0; j < colnum; j++)
	{
		char c = board[row * colnum + j];
		printf("%s", s[c]);
	}
}

void NemoLogic::PrintRow(int row)
{
	for( int j = 0 ; j < colnum ; j++ )
	{
		SetCursor(row, j*2);
		char c = board[row*colnum+j];
		printf("%s", s[c]);
	}
#if defined(_WIN32) || defined(_WIN64)
	Sleep(100);
#else
	usleep(100000);
#endif
}

void NemoLogic::PrintCol(int col)
{
	for( int j = 0 ; j < rownum ; j++ )
	{
		SetCursor(j, col*2);
		char c = board[j*colnum+col];
		printf("%s", s[c]);
	}
#if defined(_WIN32) || defined(_WIN64)
	Sleep(100);
#else
	usleep(100000);
#endif
}

int NemoLogic::GetNumbers(FILE *fi, char numbers[])
{
	int count = 0;
	char line[128];
	if( fgets(line, sizeof(line), fi) == NULL ) return 0;

	for( char *p = strtok(line, " \r\n") ; p ; p = strtok(NULL, " \r\n") )
	{
		numbers[count++] = atoi(p);
	}

	return count;
}

void NemoLogic::InitSolve()
{
	if( board ) delete[] board;
	board = new char[rownum*colnum];
	memset(board, 3, rownum*colnum*sizeof(char));
	phase = -1;

	PrintResult();
}

bool NemoLogic::Solve()
{
	if( phase == -1 )
	{
		SetFirstPattern(board, rows[0]);
		phase = 0;
	}
	if( phase == rownum )
	{
		phase--;
		while( SetNextPattern(&board[phase*colnum], rows[phase]) == false )
		{
			phase--;
			if( phase == -1 ) return false;
		}
	}
	while( true )
	{
		if( CheckPattern(phase) == true )
		{
			Print(phase);
			phase++;
			if( phase == rownum ) return true;
			SetFirstPattern(&board[phase*colnum], rows[phase]);
			continue;
		}
		while( SetNextPattern(&board[phase*colnum], rows[phase]) == false )
		{
			phase--;
			if( phase == -1 ) return false;
		}
	}
	return true;
}

bool NemoLogic::SolveN()
{
	int lastcheck = 0;
	int rowcheck[100];
	int colcheck[100];
	memset(rowcheck, 0, sizeof(rowcheck));
	memset(colcheck, 0, sizeof(colcheck));
	while( lastcheck < totalCheck )
	{
		int checked = 0;
		for( int i = 0 ; i < rownum ; i++ )
		{
			int c = CheckRow(i);
			if( c != rowcheck[i] ) { PrintRow(i); rowcheck[i] = c; }
		}
		for( int i = 0 ; i < colnum ; i++ )
		{
			int c = CheckCol(i);
			if( c != colcheck[i] ) { PrintCol(i); colcheck[i] = c; }
			checked += c;
		}
		if( lastcheck == checked ) return false;
//		PrintResult();
//		Sleep(500);
		lastcheck = checked;
	}

	return true;
}

int NemoLogic::CheckRow(int row)
{
	char t[128], r[128], u[64];
	memset(r, 0, sizeof(r));
	memset(u, 0, sizeof(u));
	int c = 0, i;
	for( i = 0 ; rows[row][i] ; i++ )
	{
		c += rows[row][i];
	}
	int s = colnum - c - i + 1;
	int p = 0;
	c = 0;
	while( true )
	{
		if( rows[row][c] == 0 )
		{
			while( p < colnum ) t[p++] = 2;
			u[c] = s;
			s = 0;
			for( i = 0 ; i < colnum ; i++ )
			{
				if( !(t[i] & board[row*colnum+i]) ) break;
			}
			if( i == colnum )
			{
				for( i = 0 ; i < colnum ; i++ )
				{
					r[i] |= t[i];
				}
			}
			do
			{
				s += u[c];
				p -= u[c];
				u[c] = 0;
				c--;
				if( c < 0 ) break;
				p -= rows[row][c]+(c!=0);
			}
			while( s == 0 );
			if( c < 0 )
			{
				c = 0;
				for( i = 0 ; i < colnum ; i++ )
				{
					board[row*colnum+i] = r[i];
					if( r[i] == 1 ) c++;
				}
				return c;
			}
			p -= u[c];
			u[c]++;
			s--;
		}
		for( i = 0 ; i < u[c]+(c != 0) ; i++ ) t[p++] = 2;
		for( i = 0 ; i < rows[row][c] ; i++ ) t[p++] = 1;
		c++;
	}
	return 0;
}

int NemoLogic::CheckCol(int col)
{
	char t[128], r[128], u[64];
	memset(r, 0, sizeof(r));
	memset(u, 0, sizeof(u));
	int c = 0, i;
	for( i = 0 ; cols[col][i] ; i++ )
	{
		c += cols[col][i];
	}
	int s = rownum - c - i + 1;
	int p = 0;
	c = 0;
	while( true )
	{
		if( cols[col][c] == 0 )
		{
			while( p < rownum ) t[p++] = 2;
			u[c] = s;
			s = 0;
			for( i = 0 ; i < rownum ; i++ )
			{
				if( !(t[i] & board[i*colnum+col]) ) break;
			}
			if( i == rownum )
			{
				for( i = 0 ; i < rownum ; i++ )
				{
					r[i] |= t[i];
				}
			}
			do
			{
				s += u[c];
				p -= u[c];
				u[c] = 0;
				c--;
				if( c < 0 ) break;
				p -= cols[col][c]+(c!=0);
			}
			while( s == 0 );
			if( c < 0 )
			{
				c = 0;
				for( i = 0 ; i < rownum ; i++ )
				{
					board[i*colnum+col] = r[i];
					if( r[i] == 1 ) c++;
				}
				return c;
			}
			p -= u[c];
			u[c]++;
			s--;
		}
		for( i = 0 ; i < u[c]+(c != 0) ; i++ ) t[p++] = 2;
		for( i = 0 ; i < cols[col][c] ; i++ ) t[p++] = 1;
		c++;
	}
	return 0;
}

void NemoLogic::SetFirstPattern(char *s, const char *p)
{
	memset(s, 2, colnum*sizeof(char));
	for( ; *p ; p++ )
	{
		for( int i = 0 ; i < *p ; i++ )
		{
			*s++ = 1;
		}
		s++;
	}
}

bool NemoLogic::SetNextPattern(char *s, const char *p)
{
	char pos[32];
	bool first = true;
	int k = 0;

	for( int i = 0 ; i < colnum ; i++ )
	{
		if( first && s[i] == 1 ) { first = false; pos[k++] = i; }
		if( s[i] != 1 ) first = true;
	}

	int c = -1;
	for( int i = 0 ; i < k ; i++ )
	{
		int t = pos[i];
		for( int j = i ; j < k ; j++ )
			t += p[j]+1;
		if( t <= colnum ) c = i;
	}

	if( c == -1 ) return false;

	s += pos[c];

	memset(s, 2, (colnum-pos[c])*sizeof(char));
	for( ; c < k ; c++ )
	{
		s++;
		for( int i = 0 ; i < p[c] ; i++ )
			*s++ = 1;
	}
	
	return true;
}

bool NemoLogic::CheckPattern(int row)
{
	if( row == rownum ) return false;

	int count;
	int k;
	for( int i = 0 ; i < colnum ; i++ )
	{
		count = 0;
		k = 0;
		for( int j = 0 ; j <= row ; j++ )
		{
			if( board[j*colnum+i] == 1 ) count++;
			else if( count > 0 )
			{
				if( count != cols[i][k] ) return false;
				count = 0;
				k++;
			}
		}
		if( row == rownum-1 && count != cols[i][k] ) return false;
		if( count > cols[i][k] ) return false;
		count = row-count;
		for( ; cols[i][k] ; k++ )
		{
			count += cols[i][k]+1;
		}
		if( count > rownum ) return false;
	}
	return true;
}

