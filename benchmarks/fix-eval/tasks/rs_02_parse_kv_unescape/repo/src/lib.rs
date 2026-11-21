use std::collections::BTreeMap;

pub fn parse_env_lines(input: &str) -> BTreeMap<String, String> {
    let mut map = BTreeMap::new();
    for raw in input.lines() {
        let line = raw.trim();
        if line.is_empty() || line.starts_with('#') {
            continue;
        }
        let parts: Vec<&str> = line.split('=').collect();
        if parts.len() == 2 {
            map.insert(parts[0].trim().to_string(), parts[1].trim().to_string());
        }
    }
    map
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn parses_values_containing_equals_and_quotes() {
        let input = r#"
# Database config
DB_URL="postgres://user:pass@host/db?sslmode=require"
TOKEN=abc==def
PLAIN=hello
"#;
        let parsed = parse_env_lines(input);
        assert_eq!(
            parsed.get("DB_URL").map(String::as_str),
            Some("postgres://user:pass@host/db?sslmode=require")
        );
        assert_eq!(parsed.get("TOKEN").map(String::as_str), Some("abc==def"));
        assert_eq!(parsed.get("PLAIN").map(String::as_str), Some("hello"));
    }
}
